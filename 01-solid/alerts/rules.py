from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date

from models.player import PlayerData, PlayerSeason


@dataclass
class AlertResult:
    is_flagged: bool
    reason: str


class ScoutingRule(ABC):
    @abstractmethod
    def check(self, player_data: PlayerData, player_season: PlayerSeason) -> AlertResult:
        pass


class LowMinutesRule(ScoutingRule):
    def __init__(self, minutes_threshold: int = 450):
        self.minutes_threshold = minutes_threshold


    def check(self, player_data: PlayerData, player_season: PlayerSeason) -> AlertResult:
        if player_season.minutes_played < self.minutes_threshold:
            return AlertResult(True, reason=f"Player has only played {player_season.minutes_played} which is less than threshold of {self.minutes_threshold} minutes")
        else:
            return AlertResult(False, reason=f"Player has played {player_season.minutes_played} which exceeds threshold of {self.minutes_threshold} minutes")


# # TODO: extend to position-specific thresholds across multiple stats in Phase 3
class StatOutlierRule(ScoutingRule):
    def __init__(self, tier_thresholds: dict[int, float] | None = None):
        self.tier_thresholds = tier_thresholds or {
            1: 0.50,
            2: 0.40,
            3: 0.32,
            4: 0.28,
        }


    def check(self, player_data: PlayerData, player_season: PlayerSeason) -> AlertResult:
        xg_threshold = self.tier_thresholds.get(player_season.league_tier, 0.35)
        xg_outlier = player_season.xg_per90 > xg_threshold
        if xg_outlier:
            return AlertResult(True, reason=f"xG/90 of {player_season.xg_per90} exceeds tier {player_season.league_tier} threshold of {xg_threshold}")
        else:
            return AlertResult(False, reason=f"xG/90 of {player_season.xg_per90} is below tier {player_season.league_tier} threshold of {xg_threshold}")


class ContractExpiryRule(ScoutingRule):
    def __init__(self, months_threshold: int = 12):
        self.months_threshold = months_threshold


    def check(self, player_data: PlayerData, player_season: PlayerSeason) -> AlertResult:
        if player_data.contract_expiry is None:
            return AlertResult(True, reason=f"{player_data.first_name} {player_data.last_name} has no current contract")
        months_remaining = (player_data.contract_expiry - date.today()).days / 30
        if months_remaining < self.months_threshold:
            return AlertResult(True, reason=f"Contract expiring on {player_data.contract_expiry} - {int(months_remaining)} months remaining")
        else:
            return AlertResult(False, reason="Contract not expiring within range")

