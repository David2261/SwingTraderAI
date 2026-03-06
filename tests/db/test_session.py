from importlib import import_module, reload
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from swingtraderai.core.config import settings
from swingtraderai.db.session import (
	AsyncSessionLocal,
	dispose_engine,
	engine,
	get_db,
	get_session,
)


@pytest.mark.asyncio
async def test_get_db_yields_session_and_closes_it():
	mock_session = AsyncMock(spec=AsyncSession)

	with patch("swingtraderai.db.session.AsyncSessionLocal") as mock_maker:
		mock_maker.return_value = mock_session

		async for db in get_db():
			assert db is mock_session

		mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_rolls_back_on_exception():
	mock_session = AsyncMock(spec=AsyncSession)
	mock_session.rollback = AsyncMock()
	mock_session.close = AsyncMock()
	mock_session.commit = AsyncMock()

	with patch("swingtraderai.db.session.AsyncSessionLocal", return_value=mock_session):
		gen = get_db()
		session = await gen.__anext__()
		await session.execute(text("SELECT 1"))

		with pytest.raises(RuntimeError):
			await gen.athrow(RuntimeError("boom inside dependency usage"))

		mock_session.rollback.assert_awaited_once()
		mock_session.close.assert_awaited_once()
		calls = [
			call[0]
			for call in mock_session.mock_calls
			if call[0] in ["rollback", "close"]
		]
		assert calls == ["rollback", "close"]


@pytest.mark.asyncio
async def test_get_session_context_manager_style():
	mock_session = AsyncMock(spec=AsyncSession)

	mock_cm = AsyncMock()
	mock_cm.__aenter__.return_value = mock_session
	mock_cm.__aexit__.return_value = None

	with patch("swingtraderai.db.session.AsyncSessionLocal", return_value=mock_cm):
		async for db in get_session():
			assert db is mock_session

		mock_cm.__aenter__.assert_awaited_once()
		mock_cm.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispose_engine_calls_engine_dispose():
	mock_engine = AsyncMock(spec=AsyncEngine)
	with patch("swingtraderai.db.session.engine", mock_engine):
		await dispose_engine()
		mock_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
async def test_engine_creation_parameters():
	with patch("swingtraderai.db.session.create_async_engine") as mock_create:
		from swingtraderai.db.session import create_engine

		create_engine()

		mock_create.assert_called_once()

		args, kwargs = mock_create.call_args
		assert args[0] == settings.DATABASE_URL
		assert kwargs.get("echo") is False
		assert kwargs.get("future") is True
		assert kwargs.get("pool_pre_ping") is True
		assert kwargs.get("pool_size") == 5
		assert kwargs.get("max_overflow") == 10
		assert kwargs.get("pool_timeout") == 30


def test_sessionmaker_configured_correctly():
	assert AsyncSessionLocal.kw.get("expire_on_commit") is False
	assert AsyncSessionLocal.class_ is AsyncSession
	session = AsyncSessionLocal()
	assert session.bind is engine


@pytest.mark.asyncio
async def test_get_db_propagates_unknown_exceptions():
	mock_session = AsyncMock(spec=AsyncSession)
	mock_session.rollback = AsyncMock()
	mock_session.close = AsyncMock()
	mock_session.commit = AsyncMock()
	mock_session.execute = AsyncMock()

	with patch("swingtraderai.db.session.AsyncSessionLocal", return_value=mock_session):
		gen = get_db()
		await gen.__anext__()

		with pytest.raises(ValueError):
			await gen.athrow(ValueError("user-land error"))

		mock_session.rollback.assert_awaited_once()
		mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_settings_validation():
	with pytest.raises(ValueError, match="DATABASE_URL is not set"):
		with patch("swingtraderai.core.config.settings.DATABASE_URL", None):
			module = import_module("swingtraderai.db.session")
			reload(module)


# @pytest.mark.asyncio
# async def test_real_db_connection_works(session):
# 	result = await session.execute(text("SELECT 1"))
# 	assert result.scalar() == 1
