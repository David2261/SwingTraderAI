from .ccxt_base import CcxtSource


class BybitSource(CcxtSource):
	def __init__(self) -> None:
		super().__init__("bybit")
		self.exchange.options["defaultType"] = "spot"
