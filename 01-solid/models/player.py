import csv
import smtplib
import sqlite3
from email.mime.text import MIMEText
from datetime import date
from dataclasses import dataclass

from enum import Enum

class Position(Enum):
    GK = "GK"
    CB = "CB"
    LB = "LB"
    RB = "RB"
    DM = "DM"
    CM = "CM"
    LW = "LW"
    RW = "RW"
    AM = "AM"
    ST = "ST"


@dataclass
class PlayerData:
    player_id: str
    first_name: str
    last_name: str
    dob: date
    nationality: str
    position: list[Position]
    current_value: int
    current_club: str
    current_club_country: str
    current_league: str
    current_league_tier: int
    contract_expiry: date | None

    @property
    def is_contract_expiring(self) -> bool:
        if self.contract_expiry is None:
            return False
        months_remaining = (self.contract_expiry - date.today()).days / 30
        return months_remaining < 12

    @property
    def is_free_agent(self) -> bool:
        return self.contract_expiry is None or self.contract_expiry < date.today()


@dataclass
class PlayerSeason:
    player_id: str
    club: str
    league_tier: int
    matches: int
    starts: int
    minutes_played: int
    goals: int
    assists: int
    goals_per90: float
    assists_per90: float
    xg_per90: float
    xa_per90: float
    progressive_carries_per90: float
    pressures_per90: float
    season: str



