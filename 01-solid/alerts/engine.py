from models.player import PlayerData


# class AlertEngine:
#     def check_alerts(self, player: Player) -> list:
#         """Checks whether this player should be flagged for any scouting alerts"""
#         alerts = []
#
#         if player.minutes_played < 450:
#             alerts.append(f"{player.first_name} {player.last_name} has low minutes: {player.minutes_played}")
#
#         today = date.today()
#         months_remaining = (player.contract_expiry - today).days / 30
#         if months_remaining < 12:
#             alerts.append(f"{self.name} contract expiring in {int(months_remaining)} months")
#
#         tier_xg_thresholds = {1: 0.5, 2: 0.4, 3: 0.3, 4: 0.25}
#         threshold = tier_xg_thresholds.get(self.league_tier, 0.3)
#         if self.xg_per90 > threshold:
#             alerts.append(f"{self.name} xG/90 of {self.xg_per90:.2f} exceeds tier threshold")
#
#         return alerts
#
#     def send_alert_email(self, recipient: str):
#         """Sends an email alert directly from this class"""
#         alerts = self.check_alerts()
#         if not alerts:
#             return
#
#         body = f"Scouting alerts for {self.name}:\n\n" + "\n".join(alerts)
#         msg = MIMEText(body)
#         msg["Subject"] = f"Scout Alert: {self.name}"
#         msg["From"] = "scout@club.com"
#         msg["To"] = recipient
#
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login("scout@club.com", "password123")
#             server.send_message(msg)