from datetime import datetime, timezone
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
from uuid6 import uuid7

from swingtraderai.schemas.market_data import (
	MARKET_DATA_SCHEMA,
	MarketDataBase,
	MarketDataOut,
	MarketDataSchema,
)


class TestMarketDataBase:
	"""Tests for MarketDataBase schema"""

	def test_market_data_base_creation(self):
		"""Test creating MarketDataBase with all fields"""
		data = MarketDataBase(
			timeframe="1h",
			open=Decimal("100.50"),
			high=Decimal("101.20"),
			low=Decimal("99.80"),
			close=Decimal("100.90"),
			volume=Decimal("1000000"),
		)
		assert data.timeframe == "1h"
		assert data.open == Decimal("100.50")
		assert data.high == Decimal("101.20")
		assert data.low == Decimal("99.80")
		assert data.close == Decimal("100.90")
		assert data.volume == Decimal("1000000")

	def test_market_data_base_optional_fields(self):
		"""Test creating MarketDataBase with only optional fields"""
		data = MarketDataBase()
		assert data.timeframe is None
		assert data.open is None
		assert data.high is None
		assert data.low is None
		assert data.close is None
		assert data.volume is None

	def test_market_data_base_with_floats(self):
		"""Test that floats are accepted and converted to Decimal"""
		data = MarketDataBase(
			open=100.50, high=101.20, low=99.80, close=100.90, volume=1000000.0
		)
		assert isinstance(data.open, Decimal)
		assert data.open == Decimal("100.50")
		assert isinstance(data.volume, Decimal)
		assert data.volume == Decimal("1000000")

	def test_market_data_base_with_strings(self):
		"""Test that string numbers are accepted"""
		data = MarketDataBase(
			open="100.50", high="101.20", low="99.80", close="100.90", volume="1000000"
		)
		assert isinstance(data.open, Decimal)
		assert data.open == Decimal("100.50")


class TestMarketDataOut:
	"""Tests for MarketDataOut schema"""

	def test_market_data_out_creation(self):
		"""Test creating MarketDataOut with all fields"""
		now = datetime.now(timezone.utc)
		ticker_id = uuid7()
		data_id = uuid7()

		data_out = MarketDataOut(
			id=data_id,
			ticker_id=ticker_id,
			timestamp=now,
			created_at=now,
			timeframe="1h",
			open=Decimal("100.50"),
			high=Decimal("101.20"),
			low=Decimal("99.80"),
			close=Decimal("100.90"),
			volume=Decimal("1000000"),
		)

		assert data_out.id == data_id
		assert data_out.ticker_id == ticker_id
		assert data_out.timestamp == now
		assert data_out.created_at == now
		assert data_out.timeframe == "1h"
		assert data_out.open == Decimal("100.50")

	def test_market_data_out_from_attributes(self):
		"""Test model_config from_attributes"""
		assert MarketDataOut.model_config["from_attributes"] is True

	def test_market_data_out_optional_fields(self):
		"""Test MarketDataOut with minimal fields"""
		now = datetime.now(timezone.utc)
		ticker_id = uuid7()
		data_id = uuid7()

		data_out = MarketDataOut(
			id=data_id, ticker_id=ticker_id, timestamp=now, created_at=now
		)

		assert data_out.timeframe is None
		assert data_out.open is None
		assert data_out.high is None


class TestMarketDataSchema:
	"""Tests for MarketDataSchema dataclass"""

	def test_singleton_instance(self):
		"""Test that MARKET_DATA_SCHEMA is a singleton"""
		assert isinstance(MARKET_DATA_SCHEMA, MarketDataSchema)

	def test_base_columns(self):
		"""Test BASE_COLUMNS contains expected columns"""
		schema = MarketDataSchema()
		expected = ["time", "open", "high", "low", "close", "volume", "timeframe"]
		assert schema.BASE_COLUMNS == expected
		assert len(schema.BASE_COLUMNS) == 7

	def test_high_low_close_columns(self):
		"""Test column name constants"""
		schema = MarketDataSchema()
		assert schema.HIGH_COLUMN == "high"
		assert schema.LOW_COLUMN == "low"
		assert schema.CLOSE_COLUMN == "close"

	def test_sql_column_types(self):
		"""Test SQL column type mappings"""
		schema = MarketDataSchema()
		assert schema.SQL_COLUMN_TYPES["open"] == "DECIMAL"
		assert schema.SQL_COLUMN_TYPES["high"] == "DECIMAL"
		assert schema.SQL_COLUMN_TYPES["low"] == "DECIMAL"
		assert schema.SQL_COLUMN_TYPES["close"] == "DECIMAL"
		assert schema.SQL_COLUMN_TYPES["volume"] == "DECIMAL"
		assert schema.SQL_COLUMN_TYPES["time"] == "TIMESTAMP"
		assert schema.SQL_COLUMN_TYPES["timestamp"] == "TIMESTAMP"

	def test_decimal_columns(self):
		"""Test DECIMAL_COLUMNS set"""
		schema = MarketDataSchema()
		expected = {"open", "high", "low", "close", "volume"}
		assert schema.DECIMAL_COLUMNS == expected

	def test_id_columns(self):
		"""Test ID_COLUMNS set"""
		schema = MarketDataSchema()
		expected = {"ticker_id", "id"}
		assert schema.ID_COLUMNS == expected

	def test_required_insert_columns(self):
		"""Test REQUIRED_INSERT_COLUMNS set"""
		schema = MarketDataSchema()
		expected = {"ticker_id", "time"}
		assert schema.REQUIRED_INSERT_COLUMNS == expected

	def test_required_indicators(self):
		"""Test REQUIRED_INDICATORS set"""
		schema = MarketDataSchema()
		expected = {"sma_10", "rsi_14", "atr_14"}
		assert schema.REQUIRED_INDICATORS == expected

	def test_unique_constraint_columns(self):
		"""Test UNIQUE_CONSTRAINT_COLUMNS list"""
		schema = MarketDataSchema()
		expected = ["ticker_id", "timeframe", "time"]
		assert schema.UNIQUE_CONSTRAINT_COLUMNS == expected

	def test_model_feature_columns(self):
		"""Test MODEL_FEATURE_COLUMNS list"""
		schema = MarketDataSchema()
		expected = ["open", "high", "low", "close", "volume"]
		assert schema.MODEL_FEATURE_COLUMNS == expected

	def test_target_column(self):
		"""Test TARGET_COLUMN constant"""
		schema = MarketDataSchema()
		assert schema.TARGET_COLUMN == "target"

	def test_time_column(self):
		"""Test TIME_COLUMN constant"""
		schema = MarketDataSchema()
		assert schema.TIME_COLUMN == "time"

	def test_drop_columns_for_training(self):
		"""Test DROP_COLUMNS_FOR_TRAINING set"""
		schema = MarketDataSchema()
		expected = {"target", "time", "future_return", "close"}
		assert schema.DROP_COLUMNS_FOR_TRAINING == expected

	def test_all_columns_property(self):
		"""Test all_columns property returns all possible columns"""
		schema = MarketDataSchema()
		all_cols = schema.all_columns

		for col in schema.BASE_COLUMNS:
			assert col in all_cols

		for col in schema.ID_COLUMNS:
			assert col in all_cols

		assert "timeframe" in all_cols
		assert "timestamp" in all_cols

	def test_get_sql_type(self):
		"""Test get_sql_type method"""
		schema = MarketDataSchema()

		assert schema.get_sql_type("open") == "DECIMAL"
		assert schema.get_sql_type("time") == "TIMESTAMP"
		assert schema.get_sql_type("unknown") == "TEXT"

	def test_is_decimal_column(self):
		"""Test is_decimal_column method"""
		schema = MarketDataSchema()

		assert schema.is_decimal_column("open") is True
		assert schema.is_decimal_column("high") is True
		assert schema.is_decimal_column("low") is True
		assert schema.is_decimal_column("close") is True
		assert schema.is_decimal_column("volume") is True
		assert schema.is_decimal_column("time") is False
		assert schema.is_decimal_column("ticker_id") is False

	def test_normalize_columns_lowercase(self):
		"""Test normalize_columns converts to lowercase"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"Open": [100.0],
				"High": [101.0],
				"Low": [99.0],
				"Close": [100.5],
				"Volume": [1000],
				"Time": [datetime.now()],
			}
		)

		normalized = schema.normalize_columns(df)

		assert "open" in normalized.columns
		assert "high" in normalized.columns
		assert "low" in normalized.columns
		assert "close" in normalized.columns
		assert "volume" in normalized.columns
		assert "time" in normalized.columns

	def test_normalize_columns_rename_datetime(self):
		"""Test normalize_columns renames datetime to time"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"open": [100.0],
				"high": [101.0],
				"low": [99.0],
				"close": [100.5],
				"volume": [1000],
				"datetime": [datetime.now()],
			}
		)

		normalized = schema.normalize_columns(df)

		assert "time" in normalized.columns
		assert "datetime" not in normalized.columns

	def test_normalize_columns_rename_timestamp(self):
		"""Test normalize_columns renames timestamp to time"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"open": [100.0],
				"high": [101.0],
				"low": [99.0],
				"close": [100.5],
				"volume": [1000],
				"timestamp": [datetime.now()],
			}
		)

		normalized = schema.normalize_columns(df)

		assert "time" in normalized.columns
		assert "timestamp" not in normalized.columns

	def test_normalize_columns_preserves_other_columns(self):
		"""Test normalize_columns preserves other columns"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"open": [100.0],
				"high": [101.0],
				"low": [99.0],
				"close": [100.5],
				"volume": [1000],
				"time": [datetime.now()],
				"extra_column": ["test"],
			}
		)

		normalized = schema.normalize_columns(df)

		assert "extra_column" in normalized.columns
		assert normalized["extra_column"].iloc[0] == "test"

	def test_validate_base_columns_success(self):
		"""Test validate_base_columns with all columns present"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"time": [datetime.now()],
				"open": [100.0],
				"high": [101.0],
				"low": [99.0],
				"close": [100.5],
				"volume": [1000],
				"timeframe": ["1h"],
			}
		)

		schema.validate_base_columns(df)

	def test_validate_base_columns_missing(self):
		"""Test validate_base_columns raises error when columns missing"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"time": [datetime.now()],
				"open": [100.0],
				"high": [101.0],
				"close": [100.5],
				"volume": [1000],
			}
		)

		with pytest.raises(ValueError) as exc_info:
			schema.validate_base_columns(df)

		assert "Отсутствуют колонки:" in str(exc_info.value)
		assert "low" in str(exc_info.value)
		assert "timeframe" in str(exc_info.value)

	def test_validate_base_columns_with_extra_columns(self):
		"""Test validate_base_columns works with extra columns"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"time": [datetime.now()],
				"open": [100.0],
				"high": [101.0],
				"low": [99.0],
				"close": [100.5],
				"volume": [1000],
				"timeframe": ["1h"],
				"extra": ["value"],
			}
		)

		schema.validate_base_columns(df)

	def test_normalize_and_validate_workflow(self):
		"""Test full workflow: normalize then validate"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"Open": [100.0],
				"High": [101.0],
				"Low": [99.0],
				"Close": [100.5],
				"Volume": [1000],
				"Datetime": [datetime.now()],
				"Timeframe": ["1h"],
			}
		)

		normalized = schema.normalize_columns(df)
		schema.validate_base_columns(normalized)

		assert "time" in normalized.columns
		assert "open" in normalized.columns
		assert "high" in normalized.columns
		assert "low" in normalized.columns
		assert "close" in normalized.columns
		assert "volume" in normalized.columns
		assert "timeframe" in normalized.columns


class TestMarketDataSchemaEdgeCases:
	"""Edge cases for MarketDataSchema"""

	def test_empty_dataframe_normalize(self):
		"""Test normalizing empty dataframe"""
		schema = MarketDataSchema()
		df = pd.DataFrame()

		normalized = schema.normalize_columns(df)

		assert normalized.empty
		assert normalized.columns.tolist() == []

	def test_empty_dataframe_validation(self):
		"""Test validating empty dataframe"""
		schema = MarketDataSchema()
		df = pd.DataFrame()

		with pytest.raises(ValueError):
			schema.validate_base_columns(df)

	def test_normalize_with_no_rename_needed(self):
		"""Test normalize with columns already in correct format"""
		schema = MarketDataSchema()
		df = pd.DataFrame(
			{
				"time": [datetime.now()],
				"open": [100.0],
				"high": [101.0],
				"low": [99.0],
				"close": [100.5],
				"volume": [1000],
				"timeframe": ["1h"],
			}
		)

		original_columns = df.columns.tolist()
		normalized = schema.normalize_columns(df)

		assert normalized.columns.tolist() == original_columns

	def test_get_sql_type_for_all_base_columns(self):
		"""Test get_sql_type for all base columns"""
		schema = MarketDataSchema()

		for col in schema.BASE_COLUMNS:
			sql_type = schema.get_sql_type(col)
			if col in schema.DECIMAL_COLUMNS:
				assert sql_type == "DECIMAL"
			elif col == "timeframe":
				assert sql_type == "TEXT"
			elif col == "time":
				assert sql_type == "TIMESTAMP"

	def test_is_decimal_column_for_all_base_columns(self):
		"""Test is_decimal_column for all base columns"""
		schema = MarketDataSchema()

		assert schema.is_decimal_column("open") is True
		assert schema.is_decimal_column("high") is True
		assert schema.is_decimal_column("low") is True
		assert schema.is_decimal_column("close") is True
		assert schema.is_decimal_column("volume") is True
		assert schema.is_decimal_column("time") is False
		assert schema.is_decimal_column("timeframe") is False

	def test_all_columns_no_duplicates(self):
		"""Test all_columns has no duplicates"""
		schema = MarketDataSchema()
		all_cols = schema.all_columns

		assert len(all_cols) == len(set(all_cols))

	def test_unique_constraint_columns_valid(self):
		"""Test unique constraint columns are valid"""
		schema = MarketDataSchema()
		unique_cols = schema.UNIQUE_CONSTRAINT_COLUMNS

		assert len(unique_cols) == 3
		assert unique_cols[0] == "ticker_id"
		assert unique_cols[1] == "timeframe"
		assert unique_cols[2] == "time"


class TestTypeAliases:
	"""Tests for type aliases"""

	def test_array_like_type_exists(self):
		"""Test that ArrayLike type alias is defined"""
		from swingtraderai.schemas.market_data import ArrayLike

		assert ArrayLike is not None
		assert isinstance(ArrayLike, type) is False

	def test_ndarray_int_type_exists(self):
		"""Test that NDArrayInt type alias is defined"""
		from swingtraderai.schemas.market_data import NDArrayInt

		assert NDArrayInt is not None


class TestMarketDataIntegration:
	"""Integration tests for MarketDataSchema with real data"""

	def test_create_complete_market_dataframe(self):
		"""Test creating a complete market dataframe"""
		schema = MARKET_DATA_SCHEMA

		dates = pd.date_range("2025-01-01", periods=100, freq="1h")
		df = pd.DataFrame(
			{
				"time": dates,
				"open": np.random.uniform(100, 110, 100),
				"high": np.random.uniform(105, 115, 100),
				"low": np.random.uniform(95, 105, 100),
				"close": np.random.uniform(100, 110, 100),
				"volume": np.random.uniform(1000000, 2000000, 100),
				"timeframe": "1h",
			}
		)

		normalized = schema.normalize_columns(df)
		schema.validate_base_columns(normalized)

		assert all(col in normalized.columns for col in schema.BASE_COLUMNS)
		assert len(normalized) == 100

	def test_dataframe_with_missing_columns(self):
		"""Test handling of dataframe with missing columns"""
		schema = MARKET_DATA_SCHEMA

		df = pd.DataFrame(
			{
				"time": pd.date_range("2025-01-01", periods=10, freq="1h"),
				"open": np.random.uniform(100, 110, 10),
				"close": np.random.uniform(100, 110, 10),
				"volume": np.random.uniform(1000000, 2000000, 10),
			}
		)

		normalized = schema.normalize_columns(df)

		with pytest.raises(ValueError) as exc_info:
			schema.validate_base_columns(normalized)

		error_msg = str(exc_info.value)
		assert "high" in error_msg
		assert "low" in error_msg
		assert "timeframe" in error_msg

	def test_decimal_conversion_workflow(self):
		"""Test that decimal columns are properly identified"""
		schema = MARKET_DATA_SCHEMA

		df = pd.DataFrame(
			{
				"time": [datetime.now(timezone.utc)],
				"open": ["100.50"],
				"high": ["101.20"],
				"low": ["99.80"],
				"close": ["100.90"],
				"volume": ["1000000"],
				"timeframe": ["1h"],
			}
		)

		schema.normalize_columns(df)

		for col in schema.DECIMAL_COLUMNS:
			assert schema.is_decimal_column(col) is True

		assert schema.is_decimal_column("time") is False
		assert schema.is_decimal_column("timeframe") is False

	def test_model_features_extraction(self):
		"""Test extracting model features"""
		schema = MARKET_DATA_SCHEMA

		df = pd.DataFrame(
			{
				"open": np.random.uniform(100, 110, 100),
				"high": np.random.uniform(105, 115, 100),
				"low": np.random.uniform(95, 105, 100),
				"close": np.random.uniform(100, 110, 100),
				"volume": np.random.uniform(1000000, 2000000, 100),
				"extra_column": "value",
			}
		)

		features = df[schema.MODEL_FEATURE_COLUMNS]

		assert features.shape[1] == 5
		assert all(col in features.columns for col in schema.MODEL_FEATURE_COLUMNS)

	def test_training_data_preparation(self):
		"""Test preparing data for training"""
		schema = MARKET_DATA_SCHEMA

		df = pd.DataFrame(
			{
				"time": pd.date_range("2025-01-01", periods=100, freq="1h"),
				"open": np.random.uniform(100, 110, 100),
				"high": np.random.uniform(105, 115, 100),
				"low": np.random.uniform(95, 105, 100),
				"close": np.random.uniform(100, 110, 100),
				"volume": np.random.uniform(1000000, 2000000, 100),
				"target": np.random.randint(0, 2, 100),
				"future_return": np.random.uniform(-0.1, 0.1, 100),
			}
		)

		X = df.drop(columns=schema.DROP_COLUMNS_FOR_TRAINING, errors="ignore")

		assert "target" not in X.columns
		assert "time" not in X.columns
		assert "future_return" not in X.columns
		assert "close" not in X.columns

	def test_unique_constraint_compliance(self):
		"""Test that dataframe can satisfy unique constraint"""
		schema = MARKET_DATA_SCHEMA

		ticker_id = uuid7()
		timeframe = "1h"
		dates = pd.date_range("2025-01-01", periods=10, freq="1h")

		df = pd.DataFrame(
			{
				"ticker_id": [ticker_id] * 10,
				"timeframe": [timeframe] * 10,
				"time": dates,
				"open": np.random.uniform(100, 110, 10),
				"high": np.random.uniform(105, 115, 10),
				"low": np.random.uniform(95, 105, 10),
				"close": np.random.uniform(100, 110, 10),
				"volume": np.random.uniform(1000000, 2000000, 10),
			}
		)

		unique_check = df.groupby(schema.UNIQUE_CONSTRAINT_COLUMNS).size()
		assert (unique_check == 1).all()

	def test_large_dataset_performance(self):
		"""Test performance with large dataset"""
		schema = MARKET_DATA_SCHEMA

		n_rows = 10000
		dates = pd.date_range("2025-01-01", periods=n_rows, freq="1min")

		df = pd.DataFrame(
			{
				"time": dates,
				"open": np.random.uniform(100, 110, n_rows),
				"high": np.random.uniform(105, 115, n_rows),
				"low": np.random.uniform(95, 105, n_rows),
				"close": np.random.uniform(100, 110, n_rows),
				"volume": np.random.uniform(1000000, 2000000, n_rows),
				"timeframe": "1min",
			}
		)

		import time

		start = time.time()

		normalized = schema.normalize_columns(df)
		schema.validate_base_columns(normalized)

		elapsed = time.time() - start
		assert elapsed < 5.0
		assert len(normalized) == n_rows

	def test_dataframe_with_nan_values(self):
		"""Test handling of NaN values"""
		schema = MARKET_DATA_SCHEMA

		df = pd.DataFrame(
			{
				"time": pd.date_range("2025-01-01", periods=10, freq="1h"),
				"open": [100.0] * 10,
				"high": [101.0] * 10,
				"low": [99.0] * 10,
				"close": [100.5] * 10,
				"volume": [1000] * 10,
				"timeframe": ["1h"] * 10,
			}
		)

		df.loc[5, "close"] = np.nan

		normalized = schema.normalize_columns(df)
		schema.validate_base_columns(normalized)

		assert normalized["close"].isna().sum() == 1
