"""
Exercise 2 — Test the VendorAlertEngine using InMemoryVendorRepository.

This is the payoff for the DIP work from Week 1.
The engine doesn't know or care whether its vendors came from a database
or an in-memory dict — it just receives a list[Vendor].

TASKS:
1. Complete all the TODO tests below
2. Write the conftest.py fixture at the bottom of this file
   (a fully-wired engine with all four rules)
3. All tests should pass before moving to Exercise 3

APPROACH:
- Each test should set up a specific scenario (one or two vendors)
- Pass those vendors directly to engine.run() — don't use the repo
  unless the test is specifically about repo integration
- Assert on the returned list of AlertResult objects
"""

import pytest

from src.alerts import (
    CancelledVendorRule,
    HighBalanceRemainingRule,
    MissingNotesRule,
    UnconfirmedDepositRule,
    VendorAlertEngine, AlertResult,
)


class TestVendorAlertEngineIsolated:
    """
    Tests for the engine's core behaviour.
    Each test uses a minimal set of vendors to keep things clear.
    """

    def test_returns_empty_list_when_no_vendors(self):
        engine = VendorAlertEngine(rules=[UnconfirmedDepositRule()])
        results = engine.run(vendors=[])
        assert results == []

    def test_returns_empty_list_when_no_rules_match(self, confirmed_venue, confirmed_band):
        # Both vendors are confirmed — UnconfirmedDepositRule should not fire
        engine = VendorAlertEngine(rules=[UnconfirmedDepositRule()])
        results = engine.run(vendors=[confirmed_venue, confirmed_band])
        assert results == []

    def test_flags_single_problematic_vendor(self, deposit_paid_photographer):
        engine = VendorAlertEngine(rules=[UnconfirmedDepositRule()])
        results = engine.run(vendors=[deposit_paid_photographer])
        assert len(results) == 1
        assert "Lens & Light" in results[0].message

    def test_flags_multiple_vendors_with_same_rule(
        self, deposit_paid_photographer, enquired_florist
    ):
        engine = VendorAlertEngine(rules=[MissingNotesRule()])
        results = engine.run(vendors=[deposit_paid_photographer, enquired_florist])
        assert len(results) == 2

    def test_multiple_rules_fire_on_same_vendor(self, deposit_paid_photographer):
        # AND MissingNotesRule AND HighBalanceRemainingRule
        engine = VendorAlertEngine(rules=[MissingNotesRule(), UnconfirmedDepositRule(), HighBalanceRemainingRule()])
        # Run all three rules against this one vendor
        results = engine.run(vendors=[deposit_paid_photographer])
        assert len(results) == 3

    def test_only_flagged_results_are_returned(self, confirmed_venue, deposit_paid_photographer):
        engine = VendorAlertEngine(rules=[UnconfirmedDepositRule()])
        results = engine.run(vendors=[deposit_paid_photographer, confirmed_venue])
        assert len(results) == 1
        assert "Lens & Light" in results[0].message

    def test_results_contain_correct_rule_names(self, cancelled_caterer):
        engine = VendorAlertEngine(rules=[CancelledVendorRule()])
        results = engine.run(vendors=[cancelled_caterer])

        assert len(results) == 1
        assert results[0].rule_name == "CancelledVendorRule"

    def test_results_contain_vendor_name_in_message(self, cancelled_caterer):
        engine = VendorAlertEngine(rules=[CancelledVendorRule()])
        results = engine.run(vendors=[cancelled_caterer])
        assert "Riverside Catering" in results[0].message


class TestVendorAlertEngineWithRepository:
    """
    Integration tests — engine pulls vendors from InMemoryVendorRepository.
    This proves the full pipeline works end-to-end without a real database.
    """

    def test_engine_processes_all_vendors_from_repo(self, vendor_repo):
        # vendor_repo has 5 vendors: confirmed_venue, deposit_paid_photographer,
        # cancelled_caterer, enquired_florist, confirmed_band
        engine = VendorAlertEngine(rules=[CancelledVendorRule()])
        vendors = vendor_repo.get_all()
        results = engine.run(vendors=vendors)

        # Only cancelled_caterer should be flagged
        assert len(results) == 1
        assert "Riverside Catering" in results[0].message

    def test_engine_with_all_rules_catches_multiple_issues(self, vendor_repo):
        engine = VendorAlertEngine(rules=[CancelledVendorRule(), UnconfirmedDepositRule(), HighBalanceRemainingRule(), MissingNotesRule()])
        results = engine.run(vendors=vendor_repo.get_all())
        assert len(results) == 7

    def test_empty_repo_produces_no_alerts(self, empty_vendor_repo):
        engine = VendorAlertEngine(rules=[CancelledVendorRule(), MissingNotesRule(), UnconfirmedDepositRule(), HighBalanceRemainingRule()])
        results = engine.run(vendors=empty_vendor_repo.get_all())
        assert results == []

    def test_engine_results_are_all_alert_result_instances(self, vendor_repo):
        engine = VendorAlertEngine(rules=[UnconfirmedDepositRule()])
        results = engine.run(vendors=vendor_repo.get_all())
        # Assert every item in results is an instance of AlertResult
        for result in results:
            assert isinstance(result, AlertResult)


class TestEngineWithFixture:

    def test_full_engine_flags_expected_vendors(self, vendor_repo, full_engine):
        results = full_engine.run(vendors=vendor_repo.get_all())
        # Assert the total number of flagged results is 7
        assert len(results) == 7