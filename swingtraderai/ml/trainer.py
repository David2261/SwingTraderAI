import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Iterator, TypeAlias
from uuid import UUID

import joblib
import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.metrics import (
	f1_score,
	roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from xgboost import XGBClassifier

from swingtraderai.db.session import get_db
from swingtraderai.indicators.matrix import add_all_indicators
from swingtraderai.schemas.market_data import MARKET_DATA_SCHEMA

ArrayLike: TypeAlias = npt.ArrayLike
NDArrayInt: TypeAlias = npt.NDArray[np.int_]


class PurgedTimeSeriesSplit(TimeSeriesSplit):
	"""TimeSeriesSplit с удалением перекрывающихся данных (purging)"""

	def __init__(self, n_splits: int = 5, purge_size: int = 5) -> None:
		super().__init__(n_splits=n_splits)
		self.purge_size = purge_size

	def split(
		self,
		X: npt.ArrayLike,
		y: npt.ArrayLike | None = None,
		groups: npt.ArrayLike | None = None,
	) -> Iterator[tuple[NDArrayInt, NDArrayInt]]:
		for train_idx, test_idx in super().split(X, y, groups):
			if self.purge_size < len(train_idx):
				train_idx = train_idx[: -self.purge_size]
			yield train_idx, test_idx


def calculate_trading_metrics(
	y_true: ArrayLike,
	y_pred_proba: ArrayLike,
	threshold: float = 0.5,
) -> Dict[str, float]:
	"""Расчет бизнес-метрик трейдинга"""
	y_true = np.asarray(y_true)
	y_pred_proba = np.asarray(y_pred_proba)

	y_pred = (y_pred_proba > threshold).astype(int)
	total_trades = int(np.sum(y_pred))

	if total_trades == 0:
		return {"win_rate": 0, "total_trades": 0, "profit_factor": 0}

	winning_trades = int(np.sum((y_pred == 1) & (y_true == 1)))
	win_rate = winning_trades / total_trades

	# Упрощенный Profit Factor через уверенность модели
	avg_win_conf = np.mean(y_pred_proba[y_true == 1]) if np.any(y_true == 1) else 0
	avg_loss_conf = np.mean(y_pred_proba[y_true == 0]) if np.any(y_true == 0) else 1
	profit_factor = (win_rate * avg_win_conf) / ((1 - win_rate) * avg_loss_conf + 1e-6)

	return {
		"win_rate": win_rate,
		"total_trades": total_trades,
		"profit_factor": float(profit_factor),
	}


async def train_model(
	ticker_id: UUID,
	timeframe: str = "1h",
	n_splits: int = 5,
	early_stopping_rounds: int = 50,
	verbose: bool = True,
) -> str:
	async with asynccontextmanager(get_db)() as session:
		cols = ", ".join(MARKET_DATA_SCHEMA.BASE_COLUMNS)
		query = text(
			f"""
			SELECT {cols}
			FROM market_data
			WHERE ticker_id = :ticker_id AND timeframe = :tf
			ORDER BY {MARKET_DATA_SCHEMA.TIME_COLUMN}
		"""
		)
		result = await session.execute(query, {"ticker_id": ticker_id, "tf": timeframe})
		rows = result.fetchall()

	if not rows:
		raise ValueError(f"Нет данных для {ticker_id}")

	df = pd.DataFrame(rows, columns=MARKET_DATA_SCHEMA.BASE_COLUMNS)
	df[MARKET_DATA_SCHEMA.TIME_COLUMN] = pd.to_datetime(
		df[MARKET_DATA_SCHEMA.TIME_COLUMN]
	)

	df = add_all_indicators(df)

	horizon = 5
	df["future_return"] = df["close"].shift(-horizon) / df["close"] - 1
	df["target"] = (df["future_return"] > 0.008).astype(int)

	df = df.dropna().reset_index(drop=True)

	if len(df) < 300:
		raise ValueError("Недостаточно данных после обработки")

	X = df.drop(columns=MARKET_DATA_SCHEMA.DROP_COLUMNS_FOR_TRAINING)
	y = df[MARKET_DATA_SCHEMA.TARGET_COLUMN]

	# Кросс-валидация с Purging
	tscv = PurgedTimeSeriesSplit(n_splits=n_splits, purge_size=horizon)
	scaler = StandardScaler()

	cv_results = []
	best_model: XGBClassifier | None = None
	best_auc: float = -1.0

	for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
		X_train_raw, X_val_raw = X.iloc[train_idx], X.iloc[val_idx]
		y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

		# Безопасное масштабирование
		X_train = scaler.fit_transform(X_train_raw)
		X_val = scaler.transform(X_val_raw)

		# Вес классов для дисбаланса
		pos_ratio = y_train.mean()
		sw = (1 - pos_ratio) / pos_ratio if pos_ratio > 0 else 1

		model = XGBClassifier(
			n_estimators=1000,
			learning_rate=0.02,
			max_depth=5,
			scale_pos_weight=sw,
			random_state=42,
			eval_metric="auc",
			early_stopping_rounds=early_stopping_rounds,
			tree_method="hist",
		)

		model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

		# Оценка
		probs = model.predict_proba(X_val)[:, 1]
		preds = model.predict(X_val)

		auc_score = float(roc_auc_score(y_val, probs))
		t_metrics = calculate_trading_metrics(y_val, probs)

		fold_metrics = {
			"fold": fold,
			"auc": auc_score,
			"win_rate": t_metrics["win_rate"],
			"trades": t_metrics["total_trades"],
			"f1": float(f1_score(y_val, preds, zero_division=0)),
		}
		cv_results.append(fold_metrics)

		if auc_score > best_auc:
			best_auc = auc_score
			best_model = model

	avg_metrics = pd.DataFrame(cv_results).mean().to_dict()
	version = datetime.now().strftime("%Y%m%d_%H%M")
	model_dir = f"models/xgboost/{ticker_id}"
	os.makedirs(model_dir, exist_ok=True)

	path = f"{model_dir}/{ticker_id}_{timeframe}_{version}.joblib"
	if best_model is None:
		raise RuntimeError("Model training failed")
	save_dict = {
		"model": best_model,
		"scaler": scaler,
		"features": [
			col
			for col in X.columns
			if col not in MARKET_DATA_SCHEMA.DROP_COLUMNS_FOR_TRAINING
		],
		"metrics": avg_metrics,
		"ticker_id": str(ticker_id),
		"timeframe": timeframe,
		"params": best_model.get_params(),
	}

	joblib.dump(save_dict, path, compress=3)

	if verbose:
		print(
			f"✅ Модель обучена. Средний AUC: {avg_metrics['auc']:.4f}, \
			WinRate: {avg_metrics['win_rate']:.2%}"
		)

	return path
