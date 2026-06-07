"""
Notification service for the Wedding Planner system.

This is the external call you'll mock in Exercise 3.
The pattern: WeddingAlertService depends on NotificationSender
via __init__ (DIP) — swap the real sender for a mock in tests,
no real emails sent.
"""

from abc import ABC, abstractmethod

from src.alerts import AlertResult


class NotificationSender(ABC):
    """Abstract base — depend on this, never on EmailNotificationSender directly."""

    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> bool:
        pass


class EmailNotificationSender(NotificationSender):
    """
    Real implementation — would send actual emails.
    Never instantiated in tests.
    """

    def send(self, recipient: str, subject: str, body: str) -> bool:
        # In production: integrate with SendGrid / SES here
        print(f"[EMAIL] To: {recipient} | Subject: {subject}")
        return True


class WeddingAlertService:
    """
    Formats alert results and sends notifications.

    Receives NotificationSender via __init__ — this is what
    makes it testable. In tests, pass a Mock() instead of
    EmailNotificationSender.
    """

    def __init__(self, sender: NotificationSender, recipient_email: str):
        self.sender = sender
        self.recipient_email = recipient_email

    def notify(self, alerts: list[AlertResult]) -> int:
        """
        Send a notification for each flagged alert.
        Returns the number of notifications sent.
        """
        sent = 0
        for alert in alerts:
            if alert.is_flagged:
                subject = f"[{alert.severity.upper()}] Wedding Alert: {alert.rule_name}"
                success = self.sender.send(
                    recipient=self.recipient_email,
                    subject=subject,
                    body=alert.message,
                )
                if success:
                    sent += 1
        return sent
