"""
Domain models for the Wedding Planner system.

These are your core data structures — every other module depends on these.
Notice how each dataclass has exactly one concern (SRP from Week 1).
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class BookingStatus(Enum):
    ENQUIRED = "enquired"
    DEPOSIT_PAID = "deposit_paid"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class VendorCategory(Enum):
    VENUE = "venue"
    CATERING = "catering"
    PHOTOGRAPHY = "photography"
    MUSIC = "music"
    FLOWERS = "flowers"
    CAKE = "cake"
    TRANSPORT = "transport"
    OTHER = "other"


@dataclass
class Vendor:
    """A supplier or service provider for the wedding."""

    id: str
    name: str
    category: VendorCategory
    quote_amount: float
    deposit_amount: float
    status: BookingStatus
    booked_date: date | None = None
    notes: str = ""

    @property
    def is_confirmed(self) -> bool:
        return self.status == BookingStatus.CONFIRMED

    @property
    def balance_remaining(self) -> float:
        if self.status == BookingStatus.DEPOSIT_PAID:
            return self.quote_amount - self.deposit_amount
        if self.status == BookingStatus.CONFIRMED:
            return 0.0
        return self.quote_amount

    @property
    def is_overdue_confirmation(self) -> bool:
        """Vendor has been at DEPOSIT_PAID status — confirmation should follow."""
        return self.status == BookingStatus.DEPOSIT_PAID and self.booked_date is None


@dataclass
class Guest:
    """A single guest invitation record."""

    id: str
    name: str
    email: str
    rsvp_confirmed: bool = False
    dietary_requirements: str = ""
    plus_one: bool = False
    table_number: int | None = None


@dataclass
class BudgetSummary:
    """Aggregated budget state — produced by the budget service, not stored directly."""

    total_budget: float
    total_quoted: float
    total_paid: float
    vendor_count: int

    @property
    def remaining_budget(self) -> float:
        return self.total_budget - self.total_quoted

    @property
    def is_over_budget(self) -> bool:
        return self.total_quoted > self.total_budget

    @property
    def percent_spent(self) -> float:
        if self.total_budget == 0:
            return 0.0
        return round((self.total_quoted / self.total_budget) * 100, 2)
