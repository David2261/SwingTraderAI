from .ccxt_base import CcxtSource


class BinanceSource(CcxtSource):
	def __init__(self) -> None:
		super().__init__("binance")
		self.exchange.options["defaultType"] = "spot"  # или 'future'
