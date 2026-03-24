from datetime import date, datetime

import pandas as pd

from swingtraderai.admin.metrics.business import (
	calculate_arppu,
	calculate_arpu,
	calculate_churn_rate,
	calculate_dau,
	calculate_growth_percentage,
	calculate_ltv_retention_based,
	calculate_ltv_simple,
	calculate_mau,
	calculate_new_users,
	calculate_retention_cohort,
	calculate_total_users,
	calculate_wau,
)


def test_calculate_total_users(registrations):
	total = calculate_total_users(registrations)
	assert total == 1000
	assert isinstance(total, int)


def test_calculate_dau(activity_df):
	target_date = date(2025, 2, 15)

	dau = calculate_dau(activity_df, target_date)
	assert isinstance(dau, int)
	assert dau > 0

	zero_dau = calculate_dau(activity_df, date(2024, 1, 1))
	assert zero_dau == 0


def test_calculate_wau(activity_df):
	target_date = date(2025, 3, 10)
	wau = calculate_wau(activity_df, target_date)

	assert isinstance(wau, int)
	assert 0 < wau <= 800


def test_calculate_mau(activity_df):
	target_date = date(2025, 3, 10)
	mau = calculate_mau(activity_df, target_date)

	assert isinstance(mau, int)
	assert 0 < mau <= 800


def test_calculate_new_users(registrations):
	start = datetime(2025, 1, 10)
	end = datetime(2025, 1, 20)

	new_users = calculate_new_users(registrations, start, end)
	assert isinstance(new_users, int)
	assert new_users >= 0


def test_calculate_growth_percentage():
	assert calculate_growth_percentage(120, 100) == 20.0
	assert calculate_growth_percentage(80, 100) == -20.0
	assert calculate_growth_percentage(105, 3) == 0.0
	assert calculate_growth_percentage(100, 0) == 0.0


def test_calculate_churn_rate():
	assert calculate_churn_rate(1000, 800, lost=150) == 15.0

	assert calculate_churn_rate(1000, 800) == 20.0
	assert calculate_churn_rate(0, 0) == 0.0


def test_calculate_retention_cohort(activity_df, registration_dict):
	d1 = calculate_retention_cohort(activity_df, registration_dict, day=1)
	assert 0.0 <= d1 <= 100.0
	assert isinstance(d1, float)

	d7 = calculate_retention_cohort(activity_df, registration_dict, day=7)
	assert 0.0 <= d7 <= 100.0


def test_calculate_arpu():
	assert calculate_arpu(5000.0, 1000) == 5.0
	assert calculate_arpu(0.0, 100) == 0.0
	assert calculate_arpu(10000.0, 0) == 0.0


def test_calculate_arppu():
	assert calculate_arppu(10000.0, 200) == 50.0
	assert calculate_arppu(5000.0, 0) == 0.0


def test_calculate_ltv_simple():
	assert calculate_ltv_simple(5.0, 12) == 60.0
	assert calculate_ltv_simple(0.0, 24) == 0.0


def test_calculate_ltv_retention_based():
	revenue = pd.Series([10.0, 8.0, 6.0, 4.0])
	retention = [1.0, 0.6, 0.4, 0.25, 0.15]

	ltv = calculate_ltv_retention_based(revenue, retention)
	assert isinstance(ltv, float)
	assert ltv > 0


def test_empty_data():
	empty_reg = pd.Series([], dtype="datetime64[ns]", name="registration_date")

	empty_activity = pd.DataFrame(
		{
			"user_id": pd.Series(dtype="int64"),
			"activity_date": pd.Series(dtype="datetime64[ns]"),
		}
	)

	assert calculate_total_users(empty_reg) == 0
	assert calculate_dau(empty_activity) == 0
	assert calculate_wau(empty_activity) == 0
	assert calculate_mau(empty_activity) == 0
	assert calculate_retention_cohort(empty_activity, {}) == 0.0


def test_calculate_dau_with_datetime_and_date(activity_df):
	"""Проверяем, что функция принимает и datetime, и date"""
	dt = datetime(2025, 2, 15)
	d = date(2025, 2, 15)

	assert calculate_dau(activity_df, dt) == calculate_dau(activity_df, d)
