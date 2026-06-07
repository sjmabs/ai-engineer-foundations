from abc import ABC, abstractmethod
from models.player import PlayerSeason

class PlayerSeasonRepository(ABC):
    @abstractmethod
    def get_by_player(self, player_id: str) -> list[PlayerSeason]:
        pass

    @abstractmethod
    def get_by_player_and_season(self, player_id: str, season: str) -> PlayerSeason | None:
        pass

    @abstractmethod
    def save(self, season: PlayerSeason) -> bool:
        pass

# need to think about the case when players change clubs, this tuple would currently overwrite
class InMemoryPlayerSeasonRepository(PlayerSeasonRepository):
    def __init__(self):
        self.player_seasons: dict[tuple[str, str], PlayerSeason] = {
            ("0004", "2021-2022"): PlayerSeason(
                player_id="0004",
                club="Norwich City",
                league_tier=2,
                matches=26,
                starts=23,
                minutes_played=2120,
                goals=0,
                assists=1,
                goals_per90=0,
                assists_per90=0.04,
                xg_per90=0.01,
                xa_per90=0.02,
                progressive_carries_per90=3.0,
                pressures_per90=5.0,
                season="2021-2022"),
            ("0004", "2023-2024"): PlayerSeason(
                player_id="0004",
                club="Ipswich Town",
                league_tier=2,
                matches=15,
                starts=8,
                minutes_played=802,
                goals=2,
                assists=2,
                goals_per90=0.22,
                assists_per90=0.22,
                xg_per90=0.1,
                xa_per90=0.05,
                progressive_carries_per90=5.0,
                pressures_per90=5.0,
                season="2023-2024"),
            ("0002", "2025-2026"): PlayerSeason(
                player_id="0002",
                club="Preston North End",
                league_tier=2,
                matches=16,
                starts=9,
                minutes_played=749,
                goals=2,
                assists=2,
                goals_per90=0.24,
                assists_per90=0.24,
                xg_per90=0.1,
                xa_per90=0.05,
                progressive_carries_per90=2.0,
                pressures_per90=7.0,
                season="2025-2026"),
        }

    def get_by_player(self, player_id: str) -> list[PlayerSeason]:
        seasons = []
        for key, season in self.player_seasons.items():
            if key[0] == player_id:
                seasons.append(season)
        return seasons

    def get_by_player_and_season(self, player_id: str, season: str) -> PlayerSeason | None:
        season_key = (player_id, season)
        return self.player_seasons.get(season_key)


    def save(self, season: PlayerSeason) -> bool:
        self.player_seasons[(season.player_id, season.season)] = season
        return True



