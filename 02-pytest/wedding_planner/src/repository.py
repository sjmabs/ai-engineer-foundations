"""
Repository layer for the Wedding Planner system.

VendorRepository is the abstract base — the test double you'll use in Week 2
exercises is InMemoryVendorRepository. Notice how this mirrors the
PlayerRepository pattern from Week 1 (DIP).
"""

from abc import ABC, abstractmethod

from src.models import BookingStatus, Guest, Vendor


class VendorRepository(ABC):
    """Abstract base — depend on this, never on the concrete implementation."""

    @abstractmethod
    def get_by_id(self, vendor_id: str) -> Vendor | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Vendor]:
        pass

    @abstractmethod
    def get_by_category(self, category) -> list[Vendor]:
        pass

    @abstractmethod
    def save(self, vendor: Vendor) -> None:
        pass


class InMemoryVendorRepository(VendorRepository):
    """
    Test double — no database required.

    Pre-loaded with realistic wedding vendor data so your tests
    have something to work with immediately.
    """

    def __init__(self, vendors: list[Vendor] | None = None):
        self._vendors: dict[str, Vendor] = {}
        if vendors:
            for v in vendors:
                self._vendors[v.id] = v

    def get_by_id(self, vendor_id: str) -> Vendor | None:
        return self._vendors.get(vendor_id)

    def get_all(self) -> list[Vendor]:
        return list(self._vendors.values())

    def get_by_category(self, category) -> list[Vendor]:
        return [v for v in self._vendors.values() if v.category == category]

    def save(self, vendor: Vendor) -> None:
        self._vendors[vendor.id] = vendor


class GuestRepository(ABC):

    @abstractmethod
    def get_all(self) -> list[Guest]:
        pass

    @abstractmethod
    def get_confirmed(self) -> list[Guest]:
        pass

    @abstractmethod
    def save(self, guest: Guest) -> None:
        pass


class InMemoryGuestRepository(GuestRepository):

    def __init__(self, guests: list[Guest] | None = None):
        self._guests: dict[str, Guest] = {}
        if guests:
            for g in guests:
                self._guests[g.id] = g

    def get_all(self) -> list[Guest]:
        return list(self._guests.values())

    def get_confirmed(self) -> list[Guest]:
        return [g for g in self._guests.values() if g.rsvp_confirmed]

    def save(self, guest: Guest) -> None:
        self._guests[guest.id] = guest
