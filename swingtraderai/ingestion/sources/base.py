from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import pandas as pd


class BaseSource(ABC):
	@abstractmethod
	def fetch_ohlcv(
		self,
		symbol: str,
		timeframe: str,
		since: Optional[datetime] = None,
		limit: int = 5000,
	) -> pd.DataFrame:
		pass
