"""
Exercise 3 — Mock the external NotificationSender.

This is the most important pattern in the whole week.
WeddingAlertService depends on NotificationSender via __init__ (DIP).
In tests, you pass a Mock() instead of EmailNotificationSender.
No real emails are sent. Tests are fast and deterministic.

TASKS:
1. Read src/notifications.py before starting
2. Complete all the TODO tests below
3. Pay attention to the difference between:
   - unittest.mock.Mock() — a generic mock
   - unittest.mock.MagicMock() — Mock with magic method support
   - unittest.mock.patch() — patches a name in a module temporarily

KEY CONCEPTS:
- mock.return_value sets what the mock returns when called
- mock.assert_called_once() asserts it was called exactly once
- mock.assert_called_with(...) asserts it was called with specific args
- mock.call_count gives you how many times it was called
"""

import pytest
from unittest.mock import MagicMock, Mock, call, patch

from src.alerts import AlertResult
from src.notifications import NotificationSender, WeddingAlertService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_sender() -> Mock:
    """A mock NotificationSender — call .send() and it returns True by default."""
    sender = Mock(spec=NotificationSender)
    sender.send.return_value = True
    return sender


@pytest.fixture
def alert_service(mock_sender) -> WeddingAlertService:
    return WeddingAlertService(sender=mock_sender, recipient_email="shaun@example.com")


@pytest.fixture
def single_critical_alert() -> AlertResult:
    return AlertResult(
        is_flagged=True,
        rule_name="CancelledVendorRule",
        message="Riverside Catering has been CANCELLED and needs replacing.",
        severity="critical",
    )


@pytest.fixture
def single_warning_alert() -> AlertResult:
    return AlertResult(
        is_flagged=True,
        rule_name="MissingNotesRule",
        message="Bloom & Blossom has no notes recorded.",
        severity="warning",
    )


@pytest.fixture
def unflagged_alert() -> AlertResult:
    return AlertResult(
        is_flagged=False,
        rule_name="UnconfirmedDepositRule",
        message="The Grand Hall confirmation status is fine.",
        severity="warning",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWeddingAlertServiceNotify:

    def test_sends_one_notification_for_one_alert(
        self, alert_service, mock_sender, single_critical_alert
    ):
        count = alert_service.notify([single_critical_alert])

        assert count == 1
        mock_sender.send.assert_called_once()

    def test_sends_to_correct_recipient(
        self, alert_service, mock_sender, single_critical_alert
    ):
        count = alert_service.notify([single_critical_alert])
        assert count == 1
        mock_sender.send.assert_called_once_with(recipient="shaun@example.com", subject=f"[{single_critical_alert.severity.upper()}] Wedding Alert: {single_critical_alert.rule_name}", body=single_critical_alert.message)

    def test_subject_contains_severity_and_rule_name(
        self, alert_service, mock_sender, single_critical_alert
    ):
        alert_service.notify([single_critical_alert])
        assert "CRITICAL" in mock_sender.send.call_args.kwargs["subject"]
        assert "CancelledVendorRule" in mock_sender.send.call_args.kwargs["subject"]


    def test_body_contains_alert_message(
        self, alert_service, mock_sender, single_critical_alert
    ):
        alert_service.notify([single_critical_alert])
        assert mock_sender.send.call_args.kwargs["body"] == single_critical_alert.message

    def test_does_not_send_for_unflagged_alert(
        self, alert_service, mock_sender, unflagged_alert
    ):
        count = alert_service.notify([unflagged_alert])
        assert count == 0 and mock_sender.call_count == 0


    def test_sends_multiple_notifications_for_multiple_alerts(
        self, alert_service, mock_sender, single_critical_alert, single_warning_alert
    ):
        count = alert_service.notify([single_critical_alert, single_warning_alert])
        assert count == 2 and mock_sender.send.call_count == 2

    def test_skips_unflagged_alerts_in_mixed_list(
        self, alert_service, mock_sender, single_critical_alert, unflagged_alert
    ):
        count = alert_service.notify([single_critical_alert, unflagged_alert])
        assert count == 1 and mock_sender.send.call_count == 1

    def test_returns_zero_for_empty_alert_list(self, alert_service, mock_sender):
        count = alert_service.notify([])
        assert count == 0
        assert mock_sender.send.call_count == 0

    def test_handles_failed_send_gracefully(
        self, alert_service, mock_sender, single_critical_alert
    ):
        mock_sender.send.return_value = False
        count = alert_service.notify([single_critical_alert])
        assert count == 0

    def test_send_called_with_correct_args_for_warning(
        self, alert_service, mock_sender, single_warning_alert
    ):
        count = alert_service.notify([single_warning_alert])
        assert count == 1 and "WARNING" in mock_sender.send.call_args.kwargs["subject"]


# ---------------------------------------------------------------------------
# Bonus: using patch() instead of injecting the mock
#
# Sometimes you can't inject the dependency via __init__.
# patch() temporarily replaces a name in a module for the duration of the test.
# ---------------------------------------------------------------------------

class TestPatchExample:

    def test_patch_sender_using_context_manager(self, single_critical_alert):
        """
        This test demonstrates unittest.mock.patch() as an alternative
        to constructor injection. You won't need this often with good DIP
        design, but it's useful to know.
        """
        with patch("src.notifications.EmailNotificationSender.send") as mock_send:
            mock_send.return_value = True
            from src.notifications import EmailNotificationSender
            service = WeddingAlertService(
                sender=EmailNotificationSender(),
                recipient_email="test@example.com"
            )
            count = service.notify([single_critical_alert])
            assert count == 1
            mock_send.assert_called_once()

