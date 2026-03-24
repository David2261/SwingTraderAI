from datetime import date, datetime
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd


def calculate_total_users(registrations: pd.Series) -> int:
	"""Total Users — всего когда-либо зарегистрированных уникальных пользователей"""
	return int(registrations.dropna().index.nunique())


def calculate_dau(
	activity_df: pd.DataFrame, target_date: Optional[Union[datetime, date]] = None
) -> int:
	"""
	DAU — уникальные пользователи за конкретный день
	activity_df должен содержать колонки: user_id, activity_date (datetime)
	"""
	if target_date is None:
		target_date = datetime.now().date()
	if isinstance(target_date, datetime):
		target = pd.Timestamp(target_date)
	else:
		target = pd.Timestamp(target_date)
	mask = activity_df["activity_date"].dt.date == target.date()
	return int(activity_df.loc[mask, "user_id"].nunique())


def calculate_wau(
	activity_df: pd.DataFrame, target_date: Optional[Union[datetime, date]] = None
) -> int:
	"""WAU — уникальные пользователи за последние 7 дней включительно"""
	if target_date is None:
		target_date = datetime.now().date()

	if isinstance(target_date, datetime):
		target = pd.Timestamp(target_date)
	else:
		target = pd.Timestamp(target_date)

	start = target - pd.Timedelta(days=6)
	end = target + pd.Timedelta(days=1)

	weekly = activity_df[
		(activity_df["activity_date"] >= start) & (activity_df["activity_date"] < end)
	]
	return int(weekly["user_id"].nunique())


def calculate_mau(
	activity_df: pd.DataFrame, target_date: Optional[Union[datetime, date]] = None
) -> int:
	"""MAU — уникальные пользователи за последние 30 дней"""
	if target_date is None:
		target_date = datetime.now().date()

	if isinstance(target_date, datetime):
		target = pd.Timestamp(target_date)
	else:
		target = pd.Timestamp(target_date)

	start = target - pd.Timedelta(days=29)
	end = target + pd.Timedelta(days=1)

	monthly = activity_df[
		(activity_df["activity_date"] >= start) & (activity_df["activity_date"] < end)
	]
	return int(monthly["user_id"].nunique())


def calculate_new_users(
	registrations: pd.Series, start_date: datetime, end_date: datetime
) -> int:
	"""Количество новых пользователей за указанный период"""
	mask = (registrations >= start_date) & (registrations < end_date)
	return int(registrations[mask].nunique())


def calculate_growth_percentage(
	current: int, previous: int, min_previous: int = 5
) -> float:
	"""Рост в % (MoM / WoW / любой другой период)"""
	if previous < min_previous:
		return 0.0
	return ((current - previous) / previous) * 100


def calculate_churn_rate(
	active_begin: int, active_end: int, lost: Optional[int] = None
) -> float:
	"""
	Churn Rate за период
	Вариант 1: lost явно передан
	Вариант 2: считаем как ушедшие = active_begin - active_end + new
	"""
	if lost is not None:
		return (lost / active_begin) * 100 if active_begin > 0 else 0.0

	return (
		((active_begin - active_end) / active_begin) * 100 if active_begin > 0 else 0.0
	)


def calculate_retention_cohort(
	activity_df: pd.DataFrame, registration_dates: Dict[int, pd.Timestamp], day: int = 1
) -> float:
	"""
	D1 / D7 / D30 retention
	day — через сколько дней после регистрации смотрим возврат
	"""
	if not registration_dates:
		return 0.0

	df = activity_df.copy()
	df["reg_date"] = df["user_id"].map(registration_dates)
	df = df.dropna(subset=["reg_date"])

	df["days_since_reg"] = (df["activity_date"] - df["reg_date"]).dt.days

	retained = df[df["days_since_reg"] == day]["user_id"].nunique()
	total = len(registration_dates)

	return (retained / total * 100) if total > 0 else 0.0


def calculate_arpu(revenue: float, total_users: int) -> float:
	"""ARPU = всего доход / все пользователи"""
	return revenue / total_users if total_users > 0 else 0.0


def calculate_arppu(revenue: float, paying_users: int) -> float:
	"""ARPPU = доход / платящие пользователи"""
	return revenue / paying_users if paying_users > 0 else 0.0


def calculate_ltv_simple(arpu: float, average_lifespan_months: float) -> float:
	"""Очень упрощённый LTV = ARPU × средняя продолжительность жизни в месяцах"""
	return arpu * average_lifespan_months


def calculate_ltv_retention_based(
	revenue_series: pd.Series,
	retention_rates: List[float],
) -> float:
	"""LTV на основе retention и среднего чека"""
	if len(retention_rates) == 0:
		return 0.0

	result = sum(revenue_series * np.array(retention_rates[: len(revenue_series)]))
	return float(result)


if __name__ == "__main__":
	dates = pd.date_range("2025-01-01", "2026-03-20", freq="D")
	users = np.random.choice(range(10000, 50000), size=5000)

	activity = pd.DataFrame(
		{
			"user_id": np.random.choice(users, size=15000),
			"activity_date": np.random.choice(dates, size=15000),
		}
	)
	registrations = pd.Series(
		np.random.choice(dates[:180], size=len(users)), index=users
	)

	print("DAU today: ", calculate_dau(activity))
	print("WAU: ", calculate_wau(activity))
	print("MAU: ", calculate_mau(activity))
	print("Total users: ", calculate_total_users(registrations))
	print("D1 retention ~ ", calculate_retention_cohort(activity, registrations, day=1))
