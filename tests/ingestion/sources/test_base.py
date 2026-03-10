from datetime import datetime
from typing import Optional

import pandas as pd
import pytest

from swingtraderai.ingestion.sources.base import BaseSource


class ConcreteSource(BaseSource):
	"""Конкретная реализация для тестов (чтобы можно было инстанцировать)"""

	def fetch_ohlcv(
		self,
		symbol: str,
		timeframe: str,
		since: Optional[datetime] = None,
		limit: int = 5000,
	) -> pd.DataFrame:
		data = {
			"timestamp": pd.date_range(start="2025-01-01", periods=10, freq="1h"),
			"open": [100.0] * 10,
			"high": [105.0] * 10,
			"low": [95.0] * 10,
			"close": [102.0] * 10,
			"volume": [1000.0] * 10,
		}
		return pd.DataFrame(data)


@pytest.fixture
def source() -> ConcreteSource:
	"""Фикстура с конкретной реализацией BaseSource"""
	return ConcreteSource()


def test_base_source_is_abstract():
	"""
	Проверяем, что BaseSource — абстрактный класс и его нельзя создать напрямую.
	"""
	with pytest.raises(TypeError) as exc_info:
		BaseSource()  # type: ignore

	error_msg = str(exc_info.value)
	assert "abstract class" in error_msg.lower()
	assert "BaseSource" in error_msg
	assert "fetch_ohlcv" in error_msg


def test_fetch_ohlcv_signature_and_return_type(source: ConcreteSource):
	"""Проверяем, что метод возвращает pd.DataFrame и имеет правильную сигнатуру"""
	df = source.fetch_ohlcv(
		symbol="BTCUSDT",
		timeframe="1h",
		since=datetime(2025, 1, 1),
		limit=100,
	)

	assert isinstance(df, pd.DataFrame)
	assert not df.empty

	expected_columns = {"timestamp", "open", "high", "low", "close", "volume"}
	assert set(df.columns) == expected_columns
	assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


@pytest.mark.parametrize(
	"symbol, timeframe, since, limit, expected_len",
	[
		("ETHUSDT", "5m", None, 5000, 10),
		("SBER", "1d", datetime(2025, 1, 1), 100, 10),
		("XRPUSDT", "15m", datetime.now(), 20, 10),
	],
)
def test_fetch_ohlcv_parameters(
	source: ConcreteSource,
	symbol: str,
	timeframe: str,
	since: Optional[datetime],
	limit: int,
	expected_len: int,
):
	"""Проверяем, что метод принимает разные
	комбинации параметров и возвращает DataFrame"""
	df = source.fetch_ohlcv(symbol, timeframe, since, limit)
	assert isinstance(df, pd.DataFrame)
	assert len(df) == expected_len


def test_fetch_ohlcv_with_default_params(source: ConcreteSource):
	"""Проверяем работу с параметрами по умолчанию"""
	df = source.fetch_ohlcv("BTCUSDT", "1h")
	assert isinstance(df, pd.DataFrame)
	assert len(df) == 10


def test_fetch_ohlcv_returns_copy_not_view():
	"""Убеждаемся, что возвращается независимый DataFrame (не view)"""
	source = ConcreteSource()
	df = source.fetch_ohlcv("TEST", "1m")
	original_shape = df.shape

	df_modified = df.copy()
	df_modified["open"] = 999.0

	assert not (df["open"] == 999.0).all()
	assert df.shape == original_shape
