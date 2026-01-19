from datetime import datetime, timedelta, timezone

from app.api.routes.billing import (
    _get_billing_period_bounds,  # pyright: ignore[reportPrivateUsage]
    _get_current_period_start,  # pyright: ignore[reportPrivateUsage]
    _normalize_billing_day,  # pyright: ignore[reportPrivateUsage]
)


class TestNormalizeBillingDay:
    """Tests for _normalize_billing_day function."""

    def test_normal_day(self):
        """Test normalization with a day that exists in the month."""
        result = _normalize_billing_day(2026, 1, 13, (7, 5, 33))
        expected = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_day_31_in_30_day_month(self):
        """Test normalization when billing day (31) exceeds days in month (30)."""
        result = _normalize_billing_day(2026, 4, 31, (7, 5, 33))
        # April has 30 days, so should normalize to April 30
        expected = datetime(2026, 4, 30, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_day_31_in_february_non_leap_year(self):
        """Test normalization for Feb 31 in non-leap year."""
        result = _normalize_billing_day(2026, 2, 31, (7, 5, 33))
        # 2026 is not a leap year, Feb has 28 days
        expected = datetime(2026, 2, 28, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_day_31_in_february_leap_year(self):
        """Test normalization for Feb 31 in leap year."""
        result = _normalize_billing_day(2024, 2, 31, (7, 5, 33))
        # 2024 is a leap year, Feb has 29 days
        expected = datetime(2024, 2, 29, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_preserves_time(self):
        """Test that billing time is preserved."""
        result = _normalize_billing_day(2026, 1, 13, (23, 59, 59))
        expected = datetime(2026, 1, 13, 23, 59, 59, tzinfo=timezone.utc)
        assert result == expected

    def test_midnight_time(self):
        """Test with midnight time."""
        result = _normalize_billing_day(2026, 1, 13, (0, 0, 0))
        expected = datetime(2026, 1, 13, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected


class TestGetCurrentPeriodStart:
    """Tests for _get_current_period_start function."""

    def test_day_after_billing_day(self):
        """Test when current day is after billing day of the month."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 13, (7, 5, 33))
        # Should return this month's billing day
        expected = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_day_before_billing_day(self):
        """Test when current day is before billing day of the month."""
        now = datetime(2026, 1, 10, 12, 0, 0, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 13, (7, 5, 33))
        # Should return previous month's billing day
        expected = datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_on_billing_day_after_billing_time(self):
        """Test when current time is on billing day but after billing time."""
        now = datetime(2026, 1, 13, 8, 0, 0, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 13, (7, 5, 33))
        # Should return this month's billing day
        expected = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_on_billing_day_before_billing_time(self):
        """Test when current time is on billing day but before billing time."""
        now = datetime(2026, 1, 13, 6, 0, 0, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 13, (7, 5, 33))
        # Should return previous month's billing day
        expected = datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_on_billing_day_at_billing_time(self):
        """Test when current time is exactly at billing time."""
        now = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 13, (7, 5, 33))
        # Should return this month's billing day (>= condition)
        expected = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_month_transition_january_to_december(self):
        """Test month transition from January to previous December."""
        now = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 13, (7, 5, 33))
        expected = datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected

    def test_with_billing_day_31_in_february(self):
        """Test with billing day 31 in February (edge case)."""
        now = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = _get_current_period_start(now, 31, (7, 5, 33))
        # February normalized to 28, then 2026/03/01 > 2026/02/28, so current month
        expected = datetime(2026, 2, 28, 7, 5, 33, tzinfo=timezone.utc)
        assert result == expected


class TestGetBillingPeriodBounds:
    """Tests for _get_billing_period_bounds function."""

    def test_current_period_mid_month(self):
        """Test CURRENT period when in the middle of the month."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 13, (7, 5, 33), now)

        assert start == datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        # End should be next month's billing day
        assert end == datetime(2026, 2, 13, 7, 5, 33, tzinfo=timezone.utc)

    def test_current_period_exactly_one_month(self):
        """Test that CURRENT period is exactly one month."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 13, (7, 5, 33), now)

        # End should be the next occurrence of day 13 at 07:05:33
        assert end.day == start.day
        assert end.hour == start.hour
        assert end.minute == start.minute
        assert end.second == start.second
        assert end.month == (start.month % 12) + 1
        assert end.year == start.year if start.month < 12 else start.year + 1

    def test_current_period_end_in_future(self):
        """Test that CURRENT period end can be in the future."""
        now = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 13, (7, 5, 33), now)

        # Start is December 13 of previous year
        assert start == datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        # End is January 13 (in future)
        assert end == datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert end > now

    def test_previous_period_month_boundaries(self):
        """Test PREVIOUS period boundaries."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("PREVIOUS", 13, (7, 5, 33), now)

        # Current period starts Jan 13, so PREVIOUS starts Dec 13
        current_period_start = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        expected_end = current_period_start - timedelta(microseconds=1)

        assert start == datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert end == expected_end

    def test_period_with_billing_day_31_april(self):
        """Test period calculation with billing day 31 in April (30 days)."""
        now = datetime(2026, 5, 15, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 31, (7, 5, 33), now)

        # April normalized to 30, May normalized to 31
        assert start.day == 30
        assert start.month == 4
        assert end.day == 31
        assert end.month == 5

    def test_previous_period_mid_month(self):
        """Test PREVIOUS period when in the middle of the month."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("PREVIOUS", 13, (7, 5, 33), now)

        # Current period is Jan 13 - Feb 13, so PREVIOUS is Dec 13 - Jan 13
        assert start == datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        # End is just before current period start
        expected_end_timestamp = datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc) - __import__(
            "datetime"
        ).timedelta(microseconds=1)
        assert end == expected_end_timestamp

    def test_current_period_december_to_january(self):
        """Test period transition from December to January."""
        now = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 13, (7, 5, 33), now)

        assert start.year == 2025
        assert start.month == 12
        assert end.year == 2026
        assert end.month == 1

    def test_current_period_january_to_february_leap_year(self):
        """Test period transition from January to February in leap year."""
        # Now is Jan 20, billing day 31, we haven't reached it yet
        now = datetime(2024, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 31, (7, 5, 33), now)

        # Since we're before the 31st, current period started last month (Dec 31)
        assert start == datetime(2023, 12, 31, 7, 5, 33, tzinfo=timezone.utc)
        # February has 29 days in 2024 (leap year), normalized from day 31
        assert end == datetime(2024, 1, 31, 7, 5, 33, tzinfo=timezone.utc)

    def test_current_period_january_to_february_non_leap_year(self):
        """Test period transition from January to February in non-leap year."""
        # Now is Jan 20, billing day 31, we haven't reached it yet
        now = datetime(2025, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 31, (7, 5, 33), now)

        # Since we're before the 31st, current period started last month (Dec 31)
        assert start == datetime(2024, 12, 31, 7, 5, 33, tzinfo=timezone.utc)
        # February has 28 days in 2025 (non-leap year), normalized from day 31
        assert end == datetime(2025, 1, 31, 7, 5, 33, tzinfo=timezone.utc)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_billing_day_1(self):
        """Test with billing day 1 (start of month)."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 1, (7, 5, 33), now)

        assert start == datetime(2026, 1, 1, 7, 5, 33, tzinfo=timezone.utc)
        assert end == datetime(2026, 2, 1, 7, 5, 33, tzinfo=timezone.utc)

    def test_billing_time_midnight(self):
        """Test with billing time at midnight."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 13, (0, 0, 0), now)

        assert start == datetime(2026, 1, 13, 0, 0, 0, tzinfo=timezone.utc)
        assert end == datetime(2026, 2, 13, 0, 0, 0, tzinfo=timezone.utc)

    def test_billing_time_end_of_day(self):
        """Test with billing time near end of day."""
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        start, end = _get_billing_period_bounds("CURRENT", 13, (23, 59, 59), now)

        assert start == datetime(2026, 1, 13, 23, 59, 59, tzinfo=timezone.utc)
        assert end == datetime(2026, 2, 13, 23, 59, 59, tzinfo=timezone.utc)

    def test_february_leap_year_context_string(self):
        """Test from the actual customer support message."""
        # Customer: Dec 13, 2025 at 07:05:33 AM UTC
        # Current date (from requirements): Jan 19, 2026
        access_timestamp = datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        now = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)

        # On Jan 19, the CURRENT period is Jan 13 - Feb 13 (we're past the 13th)
        start, end = _get_billing_period_bounds(
            "CURRENT",
            access_timestamp.day,
            (access_timestamp.hour, access_timestamp.minute, access_timestamp.second),
            now,
        )

        assert start == datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert end == datetime(2026, 2, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert end > now  # End is in the future

        # The PREVIOUS period would be the first billing period (Dec 13 - Jan 13)
        prev_start, prev_end = _get_billing_period_bounds(
            "PREVIOUS",
            access_timestamp.day,
            (access_timestamp.hour, access_timestamp.minute, access_timestamp.second),
            now,
        )
        assert prev_start == datetime(2025, 12, 13, 7, 5, 33, tzinfo=timezone.utc)
        assert prev_end == datetime(2026, 1, 13, 7, 5, 33, tzinfo=timezone.utc) - __import__(
            "datetime"
        ).timedelta(microseconds=1)
