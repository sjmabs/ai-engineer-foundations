"""
Wedding planning alert rules engine.

This mirrors the AnomalyDetectionEngine from Week 1.
Each rule is isolated, testable, and the engine never needs
changing when new rules are added (OCP).

Your Week 2 exercises focus on testing every rule in isolation
and testing the engine as a whole using InMemoryVendorRepository.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models import BudgetSummary, Vendor


@dataclass
class AlertResult:
    """The output of a single rule check."""

    is_flagged: bool
    rule_name: str
    message: str
    severity: str = "warning"  # "warning" | "critical"


class VendorAlertRule(ABC):
    """Abstract base — every rule implements this interface."""

    @abstractmethod
    def check(self, vendor: Vendor) -> AlertResult:
        pass


class UnconfirmedDepositRule(VendorAlertRule):
    """
    Flag vendors where a deposit has been paid but no confirmation received.

    In practice: you've paid money but haven't had written confirmation back.
    This is a real risk — you want to catch it early.
    """

    def check(self, vendor: Vendor) -> AlertResult:
        flagged = vendor.is_overdue_confirmation
        return AlertResult(
            is_flagged=flagged,
            rule_name="UnconfirmedDepositRule",
            message=(
                f"{vendor.name} has a deposit paid but no booking confirmation on record."
                if flagged
                else f"{vendor.name} confirmation status is fine."
            ),
            severity="critical",
        )


class HighBalanceRemainingRule(VendorAlertRule):
    """
    Flag vendors with a large outstanding balance.

    Threshold: balance is over 50% of the original quote amount.
    Useful for flagging vendors that need to be paid soon.
    """

    def __init__(self, threshold_percent: float = 0.5):
        self.threshold_percent = threshold_percent

    def check(self, vendor: Vendor) -> AlertResult:
        threshold = vendor.quote_amount * self.threshold_percent
        flagged = vendor.balance_remaining > threshold
        return AlertResult(
            is_flagged=flagged,
            rule_name="HighBalanceRemainingRule",
            message=(
                f"{vendor.name} has £{vendor.balance_remaining:.2f} outstanding "
                f"({self.threshold_percent * 100:.0f}%+ of quote)."
                if flagged
                else f"{vendor.name} balance is within acceptable range."
            ),
            severity="warning",
        )


class CancelledVendorRule(VendorAlertRule):
    """
    Flag any vendor that has been cancelled.

    Cancelled vendors need replacing — this surfaces them immediately
    rather than letting them go unnoticed in a list.
    """

    def check(self, vendor: Vendor) -> AlertResult:
        from src.models import BookingStatus

        flagged = vendor.status == BookingStatus.CANCELLED
        return AlertResult(
            is_flagged=flagged,
            rule_name="CancelledVendorRule",
            message=(
                f"{vendor.name} has been CANCELLED and needs replacing."
                if flagged
                else f"{vendor.name} is not cancelled."
            ),
            severity="critical",
        )


class MissingNotesRule(VendorAlertRule):
    """
    Flag vendors with no notes recorded.

    Low severity — but useful for ensuring every vendor has
    at least some context recorded (contact details, agreed terms, etc.)
    """

    def check(self, vendor: Vendor) -> AlertResult:
        flagged = not vendor.notes.strip()
        return AlertResult(
            is_flagged=flagged,
            rule_name="MissingNotesRule",
            message=(
                f"{vendor.name} has no notes recorded — add contact details and agreed terms."
                if flagged
                else f"{vendor.name} has notes on record."
            ),
            severity="warning",
        )


class BudgetAlertRule(ABC):
    """Separate interface for budget-level rules (not per-vendor)."""

    @abstractmethod
    def check(self, summary: BudgetSummary) -> AlertResult:
        pass


class OverBudgetRule(BudgetAlertRule):
    """Flag when total quoted spend exceeds the wedding budget."""

    def check(self, summary: BudgetSummary) -> AlertResult:
        flagged = summary.is_over_budget
        return AlertResult(
            is_flagged=flagged,
            rule_name="OverBudgetRule",
            message=(
                f"Total quoted spend (£{summary.total_quoted:.2f}) exceeds budget "
                f"(£{summary.total_budget:.2f}) by £{abs(summary.remaining_budget):.2f}."
                if flagged
                else f"Budget is on track — £{summary.remaining_budget:.2f} remaining."
            ),
            severity="critical",
        )


class NearBudgetLimitRule(BudgetAlertRule):
    """Flag when quoted spend is within 10% of the total budget."""

    def __init__(self, warning_threshold: float = 0.9):
        self.warning_threshold = warning_threshold

    def check(self, summary: BudgetSummary) -> AlertResult:
        flagged = (
            not summary.is_over_budget
            and summary.percent_spent >= self.warning_threshold * 100
        )
        return AlertResult(
            is_flagged=flagged,
            rule_name="NearBudgetLimitRule",
            message=(
                f"Approaching budget limit — {summary.percent_spent}% of budget committed."
                if flagged
                else f"Budget usage is {summary.percent_spent}% — within safe range."
            ),
            severity="warning",
        )


class VendorAlertEngine:
    """
    Runs all registered vendor rules against every vendor in the repository.

    This is the engine you'll test in Exercise 2 using InMemoryVendorRepository.
    It never needs changing when new rules are added — just pass in different rules.
    """

    def __init__(self, rules: list[VendorAlertRule]):
        self.rules = rules

    def run(self, vendors: list[Vendor]) -> list[AlertResult]:
        results = []
        for vendor in vendors:
            for rule in self.rules:
                result = rule.check(vendor)
                if result.is_flagged:
                    results.append(result)
        return results
