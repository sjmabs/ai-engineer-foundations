from models.player import Player


def generate_scouting_report(self, player: Player, ) -> str:
    """Generates and prints a scouting report for this player"""
    alerts = self.check_alerts()
    report = f"""
        SCOUTING REPORT — {self.name.upper()}
        Position: {self.position} | Club: {self.current_club} | Tier: {self.league_tier}
        Value: £{self.transfermarkt_value_gbp:,} | Contract expires: {self.contract_expiry}

        SEASON STATS ({self.season})
        Minutes: {self.minutes_played} | Goals: {self.goals} | Assists: {self.assists}
        xG/90: {self.xg_per90:.2f} | xA/90: {self.xa_per90:.2f}
        Progressive carries/90: {self.progressive_carries_per90:.2f}
        Pressures/90: {self.pressures_per90:.2f}

        ALERTS
        {"No alerts." if not alerts else chr(10).join(f"- {a}" for a in alerts)}
                """
    print(report)
    return report