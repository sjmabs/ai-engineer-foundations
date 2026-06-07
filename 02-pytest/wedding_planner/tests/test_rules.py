"""
Exercise 1 — Test each alert rule in isolation.

Each rule should be tested independently with a known Vendor instance.
The conftest.py fixtures give you pre-built vendors to work with.

TASKS:
1. Run the existing passing tests first: pytest tests/test_rules.py -v
2. Complete all the TODO tests below
3. Add @pytest.mark.parametrize to the threshold tests at the bottom
4. All tests should pass before moving to Exercise 2

HINT: You're testing one rule at a time. Each rule's check() method
returns an AlertResult with is_flagged: bool and message: str.
Assert both — don't just assert is_flagged.
"""

import pytest
from datetime import date

from src.alerts import (
    CancelledVendorRule,
    HighBalanceRemainingRule,
    MissingNotesRule,
    OverBudgetRule,
    NearBudgetLimitRule,
    UnconfirmedDepositRule,
)
from src.models import BookingStatus, BudgetSummary, Vendor, VendorCategory


# ---------------------------------------------------------------------------
# UnconfirmedDepositRule
# ---------------------------------------------------------------------------

class TestUnconfirmedDepositRule:

    def test_flags_deposit_paid_with_no_booking_date(self, deposit_paid_photographer):
        rule = UnconfirmedDepositRule()
        result = rule.check(deposit_paid_photographer)

        assert result.is_flagged is True
        assert "Lens & Light Photography" in result.message
        assert result.severity == "critical"

    def test_does_not_flag_confirmed_vendor(self, confirmed_venue):
        rule = UnconfirmedDepositRule()
        result = rule.check(confirmed_venue)
        assert result.is_flagged is False
        assert "fine" in result.message

    def test_does_not_flag_enquired_vendor(self, enquired_florist):
        rule = UnconfirmedDepositRule()
        result = rule.check(enquired_florist)
        assert result.is_flagged is False
        assert "fine" in result.message


# ---------------------------------------------------------------------------
# HighBalanceRemainingRule
# ---------------------------------------------------------------------------

class TestHighBalanceRemainingRule:

    def test_flags_vendor_with_large_balance(self, deposit_paid_photographer):
        # photographer: quote=3500, deposit=500, balance=3000 (85% remaining)
        # Default threshold is 50% — should be flagged
        rule = HighBalanceRemainingRule()
        result = rule.check(deposit_paid_photographer)
        assert result.is_flagged is True
        assert "£3000.00" in result.message

    def test_does_not_flag_fully_paid_vendor(self, confirmed_band):
        rule = HighBalanceRemainingRule()
        result = rule.check(confirmed_band)
        assert result.is_flagged is False
        assert "within acceptable range" in result.message


    def test_does_not_flag_vendor_below_threshold(self, confirmed_venue):
        rule = HighBalanceRemainingRule()
        result = rule.check(confirmed_venue)
        assert result.is_flagged is False
        assert "within acceptable range" in result.message

    # ------------------------------------------------------------------
    # PARAMETRIZE TASK
    # Replace this single test with @pytest.mark.parametrize covering:
    # - threshold=0.9, balance=3000 (85%) → NOT flagged (below threshold)
    # - threshold=0.8, balance=3000 (85%) → flagged (above threshold)
    # - threshold=0.5, balance=3000 (85%) → flagged (above threshold)
    # - threshold=0.5, balance=1000 (28%) → NOT flagged
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("threshold, deposit, flagged, message", [(0.9, 500, False, "within acceptable range"), (0.8, 500, True, "outstanding"), (0.5, 500, True, "outstanding"), (0.5, 2600, False, "within acceptable range")] )
    def test_threshold_behaviour(self, threshold, deposit, flagged, message):
        vendor = Vendor(
            id="test",
            name="Test Vendor",
            category=VendorCategory.OTHER,
            quote_amount=3500,
            deposit_amount=deposit,
            status=BookingStatus.DEPOSIT_PAID,
            notes="test",
        )
        rule = HighBalanceRemainingRule(threshold)
        result = rule.check(vendor)
        assert result.is_flagged is flagged
        assert message in result.message


# ---------------------------------------------------------------------------
# CancelledVendorRule
# ---------------------------------------------------------------------------

class TestCancelledVendorRule:

    def test_flags_cancelled_vendor(self, cancelled_caterer):
        rule = CancelledVendorRule()
        result = rule.check(cancelled_caterer)
        assert result.is_flagged is True
        assert "has been CANCELLED" in result.message

    def test_does_not_flag_confirmed_vendor(self, confirmed_venue):
        # TODO
        rule = CancelledVendorRule()
        result = rule.check(confirmed_venue)
        assert result.is_flagged is False
        assert "is not cancelled" in result.message

    def test_does_not_flag_enquired_vendor(self, enquired_florist):
        rule = CancelledVendorRule()
        result = rule.check(enquired_florist)
        assert result.is_flagged is False
        assert "is not cancelled" in result.message


# ---------------------------------------------------------------------------
# MissingNotesRule
# ---------------------------------------------------------------------------

class TestMissingNotesRule:

    def test_flags_vendor_with_empty_notes(self, enquired_florist):
        rule = MissingNotesRule()
        result = rule.check(enquired_florist)
        assert result.is_flagged is True
        assert result.severity == "warning"
        assert "has no notes recorded" in result.message

    def test_flags_vendor_with_whitespace_only_notes(self, deposit_paid_photographer):
        rule = MissingNotesRule()
        result = rule.check(deposit_paid_photographer)
        assert result.is_flagged is True
        assert result.severity == "warning"
        assert "has no notes recorded" in result.message


    def test_does_not_flag_vendor_with_notes(self, confirmed_venue):
        rule = MissingNotesRule()
        result = rule.check(confirmed_venue)
        assert result.is_flagged is False
        assert "has notes on record" in result.message


# ---------------------------------------------------------------------------
# Budget rules
# ---------------------------------------------------------------------------

class TestOverBudgetRule:

    def test_flags_when_over_budget(self):
        summary = BudgetSummary(
            total_budget=10000.0,
            total_quoted=12000.0,
            total_paid=5000.0,
            vendor_count=3,
        )
        rule = OverBudgetRule()
        result = rule.check(summary)

        assert result.is_flagged is True
        assert "£2000.00" in result.message
        assert result.severity == "critical"
        assert "exceeds budget" in result.message

    def test_does_not_flag_when_under_budget(self):
        summary = BudgetSummary(
            total_budget=14000.0,
            total_quoted=12000.0,
            total_paid=5000.0,
            vendor_count=3,
        )
        rule = OverBudgetRule()
        result = rule.check(summary)
        assert result.is_flagged is False
        assert "Budget is on track" in result.message

    def test_does_not_flag_when_exactly_on_budget(self):
        summary = BudgetSummary(
            total_budget=12000.0,
            total_quoted=12000.0,
            total_paid=5000.0,
            vendor_count=3,
        )
        rule = OverBudgetRule()
        result = rule.check(summary)
        assert result.is_flagged is False
        assert "Budget is on track" in result.message


class TestNearBudgetLimitRule:
    @pytest.mark.parametrize("quoted,budget,flagged,message", [
        pytest.param(9500,10000,True,"Approaching budget limit", id="near_limit"),
        pytest.param(9000,10000,True,"Approaching budget limit", id="on_threshold"),
        pytest.param(8999,10000, False,"within safe range", id="under_threshold"),
        pytest.param(10500,10000,False,"within safe range", id="over_budget")])
    def test_flags_when_near_limit(self, quoted, budget, flagged, message):
        summary = BudgetSummary(
            total_budget=budget,
            total_quoted=quoted,
            total_paid=5000.0,
            vendor_count=3,
        )
        rule = NearBudgetLimitRule()
        result = rule.check(summary)
        assert result.is_flagged is flagged
        assert message in result.message

