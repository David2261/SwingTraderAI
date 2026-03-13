from typing import cast

from swingtraderai.tasks.ingestion import ingest_ohlcv


def run_full_pipeline(symbol: str, timeframe: str, source: str = "moex") -> str:
	"""Здесь потом будет: ingest → calculate indicators → run ML → send signal"""
	task = ingest_ohlcv.delay(symbol, timeframe, source)
	return cast(str, task.id)
