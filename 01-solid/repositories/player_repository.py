from abc import ABC, abstractmethod
from datetime import date

from models.player import Position, PlayerData


class PlayerRepository(ABC):
    @abstractmethod
    def get_by_id(self, player_id: str) -> PlayerData | None:
        pass

    @abstractmethod
    def get_by_position(self, position: Position) -> list[PlayerData]:
        pass

    @abstractmethod
    def save(self, player: PlayerData) -> bool:
        pass


class InMemoryPlayerRepository(PlayerRepository):
    def __init__(self):
        self.players: dict[str, PlayerData] = {
            "0001": PlayerData(
            player_id="0001",
            first_name="Richard",
            last_name="Kone",
            dob= date(2003 , 7, 15),
            nationality="Côte d'Ivoire",
            position = [Position("ST")],
            current_club="Queens Park Rangers",
            current_club_country="England",
            current_league="Championship",
            current_league_tier=2,
            contract_expiry=date(2030, 6, 30),
            current_value=5000000
            ),
            "0002": PlayerData(
                player_id="0002",
                first_name="Brad",
                last_name="Potts",
                dob=date(1994, 7, 3),
                nationality="England",
                position=[Position("DM"), Position("AM"), Position("CM"), Position("RB")],
                current_club="Preston North End",
                current_club_country="England",
                current_league="Championship",
                current_league_tier=2,
                contract_expiry=date(2026, 6, 30),
                current_value=800000
            ),
            "0003": PlayerData(
                player_id="0003",
                first_name="George",
                last_name="Broadbent",
                dob=date(2000, 9, 30),
                nationality="England",
                position=[Position("DM"), Position("CB"), Position("CM")],
                current_club="Doncaster Rovers",
                current_club_country="England",
                current_league="League Two",
                current_league_tier=4,
                contract_expiry=date(2027, 6, 30),
                current_value=275000
            ),
            "0004": PlayerData(
                player_id="0004",
                first_name="Brandon",
                last_name="Williams",
                dob=date(2000, 9, 3),
                nationality="England",
                position=[Position("LB")],
                current_club="Hull City",
                current_club_country="England",
                current_league="Championship",
                current_league_tier=2,
                contract_expiry=None,
                current_value=800000
            )
        }



    def get_by_id(self, player_id: str) -> PlayerData | None:
        return self.players.get(player_id)

    def get_by_position(self, position: Position) -> list[PlayerData]:
        player_search = []
        for player in self.players.values():
            if position in player.position:
                player_search.append(player)
        return player_search

    def save(self, player: PlayerData) -> bool:
        self.players[player.player_id] = player
        return True

