"""
conftest.py — shared pytest fixtures for the wedding planner test suite.

These fixtures are available to every test file automatically.
No imports needed — pytest picks them up from conftest.py.

Your exercises this week will use these fixtures as a starting point
and add their own as needed.
"""

import pytest
from datetime import date

from src.models import BookingStatus, Guest, Vendor, VendorCategory
from src.repository import InMemoryGuestRepository, InMemoryVendorRepository
from src.alerts import VendorAlertEngine, UnconfirmedDepositRule, HighBalanceRemainingRule, CancelledVendorRule, \
    MissingNotesRule


# ---------------------------------------------------------------------------
# Vendor fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def confirmed_venue() -> Vendor:
    return Vendor(
        id="v001",
        name="The Grand Hall",
        category=VendorCategory.VENUE,
        quote_amount=8000.0,
        deposit_amount=2000.0,
        status=BookingStatus.CONFIRMED,
        booked_date=date(2025, 3, 15),
        notes="Main hall + garden. Contact: Sarah 07700 900123",
    )


@pytest.fixture
def deposit_paid_photographer() -> Vendor:
    """Deposit paid but no confirmation — should trigger UnconfirmedDepositRule."""
    return Vendor(
        id="v002",
        name="Lens & Light Photography",
        category=VendorCategory.PHOTOGRAPHY,
        quote_amount=3500.0,
        deposit_amount=500.0,
        status=BookingStatus.DEPOSIT_PAID,
        booked_date=None,  # <-- no confirmation yet
        notes="",
    )


@pytest.fixture
def cancelled_caterer() -> Vendor:
    """Cancelled vendor — should trigger CancelledVendorRule."""
    return Vendor(
        id="v003",
        name="Riverside Catering",
        category=VendorCategory.CATERING,
        quote_amount=6000.0,
        deposit_amount=0.0,
        status=BookingStatus.CANCELLED,
        notes="Cancelled — went out of business",
    )


@pytest.fixture
def enquired_florist() -> Vendor:
    """Just enquired, no deposit — no notes recorded."""
    return Vendor(
        id="v004",
        name="Bloom & Blossom",
        category=VendorCategory.FLOWERS,
        quote_amount=1200.0,
        deposit_amount=0.0,
        status=BookingStatus.ENQUIRED,
        notes="",  # <-- should trigger MissingNotesRule
    )


@pytest.fixture
def confirmed_band() -> Vendor:
    return Vendor(
        id="v005",
        name="The Jazz Collective",
        category=VendorCategory.MUSIC,
        quote_amount=2500.0,
        deposit_amount=2500.0,
        status=BookingStatus.CONFIRMED,
        booked_date=date(2025, 4, 1),
        notes="4-piece band. Set list agreed. Final payment on the day.",
    )


@pytest.fixture
def all_vendors(
    confirmed_venue,
    deposit_paid_photographer,
    cancelled_caterer,
    enquired_florist,
    confirmed_band,
) -> list[Vendor]:
    """All five vendors as a list — useful for engine tests."""
    return [
        confirmed_venue,
        deposit_paid_photographer,
        cancelled_caterer,
        enquired_florist,
        confirmed_band,
    ]


# ---------------------------------------------------------------------------
# Repository fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vendor_repo(all_vendors) -> InMemoryVendorRepository:
    """Populated in-memory vendor repository — your test double."""
    return InMemoryVendorRepository(vendors=all_vendors)


@pytest.fixture
def empty_vendor_repo() -> InMemoryVendorRepository:
    return InMemoryVendorRepository()


# ---------------------------------------------------------------------------
# Guest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def confirmed_guest() -> Guest:
    return Guest(
        id="g001",
        name="Alice Johnson",
        email="alice@example.com",
        rsvp_confirmed=True,
        dietary_requirements="Vegetarian",
        plus_one=True,
        table_number=3,
    )


@pytest.fixture
def unconfirmed_guest() -> Guest:
    return Guest(
        id="g002",
        name="Bob Smith",
        email="bob@example.com",
        rsvp_confirmed=False,
    )


@pytest.fixture
def guest_repo(confirmed_guest, unconfirmed_guest) -> InMemoryGuestRepository:
    return InMemoryGuestRepository(guests=[confirmed_guest, unconfirmed_guest])


## engine
@pytest.fixture
def full_engine() -> VendorAlertEngine:
    """Engine wired with all four vendor rules."""
    return VendorAlertEngine(rules=[
        UnconfirmedDepositRule(),
        HighBalanceRemainingRule(),
        CancelledVendorRule(),
        MissingNotesRule(),
    ])
