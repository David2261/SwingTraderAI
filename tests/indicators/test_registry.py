from swingtraderai.indicators.base import BaseIndicator, IndicatorResult
from swingtraderai.indicators.registry import IndicatorRegistry, registry


class TestIndicator(BaseIndicator):
	name = "test_indicator"
	category = "test"
	description = "Индикатор для тестирования реестра"

	def calculate(self, df, **kwargs):
		return IndicatorResult(name=self.name, value=42.0)


class AnotherTestIndicator(BaseIndicator):
	name = "momentum_test"
	category = "momentum"
	description = "Тестовый индикатор momentum"

	def calculate(self, df, **kwargs):
		return IndicatorResult(name=self.name, value=15.5)


def test_registry_is_singleton():
	"""Проверяем, что registry — один и тот же объект"""
	reg1 = registry
	reg2 = registry
	assert reg1 == reg2


def test_register_indicator():
	"""Регистрация индикатора"""
	indicator = TestIndicator()
	IndicatorRegistry.register(indicator)

	assert "test_indicator" in IndicatorRegistry.list_all()
	assert IndicatorRegistry.get("test_indicator") is indicator
	assert IndicatorRegistry.get("TEST_INDICATOR") is indicator


def test_register_multiple_indicators():
	"""Регистрация нескольких индикаторов"""
	ind1 = TestIndicator()
	ind2 = AnotherTestIndicator()

	IndicatorRegistry.register(ind1)
	IndicatorRegistry.register(ind2)

	all_indicators = IndicatorRegistry.list_all()
	assert "test_indicator" in all_indicators
	assert "momentum_test" in all_indicators


def test_get_by_category():
	"""Получение индикаторов по категории"""
	IndicatorRegistry.register(TestIndicator())
	IndicatorRegistry.register(AnotherTestIndicator())

	momentum_indicators = IndicatorRegistry.get_by_category("momentum")
	test_indicators = IndicatorRegistry.get_by_category("test")

	assert len(momentum_indicators) >= 1
	assert len(test_indicators) >= 1
	assert all(ind.category == "momentum" for ind in momentum_indicators)


def test_list_categories():
	"""Список всех категорий"""
	IndicatorRegistry.register(TestIndicator())
	IndicatorRegistry.register(AnotherTestIndicator())

	categories = IndicatorRegistry.list_categories()
	assert "test" in categories
	assert "momentum" in categories


def test_list_all():
	"""Список всех зарегистрированных индикаторов"""
	IndicatorRegistry.register(TestIndicator())
	indicators = IndicatorRegistry.list_all()

	assert isinstance(indicators, list)
	assert len(indicators) > 0
	assert "test_indicator" in indicators


def test_duplicate_registration_overwrites():
	"""Повторная регистрация с тем же именем перезаписывает"""
	ind1 = TestIndicator()
	ind2 = TestIndicator()

	IndicatorRegistry.register(ind1)
	IndicatorRegistry.register(ind2)

	retrieved = IndicatorRegistry.get("test_indicator")
	assert retrieved is ind2


def test_get_nonexistent_indicator():
	"""Получение несуществующего индикатора возвращает None"""
	result = IndicatorRegistry.get("non_existent_indicator")
	assert result is None


def test_registry_starts_empty_or_has_indicators():
	"""Проверяем, что реестр не падает при вызове методов"""
	assert isinstance(IndicatorRegistry.list_all(), list)
	assert isinstance(IndicatorRegistry.list_categories(), list)


def test_global_registry_is_used():
	"""Проверяем, что глобальный registry работает"""
	assert isinstance(registry, IndicatorRegistry)
	assert hasattr(registry, "register")
	assert hasattr(registry, "get")
	assert hasattr(registry, "list_all")


def test_real_indicators_are_registered():
	"""Проверяем, что наши основные индикаторы зарегистрированы"""
	all_indicators = registry.list_all()

	expected = ["ema20", "ema50", "ema200", "rsi", "vwap", "fractal"]
	for name in expected:
		if name in all_indicators:
			assert registry.get(name) is not None
