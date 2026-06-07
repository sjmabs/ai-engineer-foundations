from repositories.player_repository import PlayerRepository
# not used

class FbrefIngester:
    def __init__(self, source):
        pass

    def load_from_fbref(self, raw: dict):
        """Scrapes and parses FBref data directly into this object"""

        self.minutes_played = int(raw.get("minutes", 0))
        self.goals = int(raw.get("goals", 0))
        self.assists = int(raw.get("assists", 0))
        self.season = raw.get("season", "")

        minutes_per90 = self.minutes_played / 90 if self.minutes_played > 0 else 1
        self.xg_per90 = float(raw.get("xg", 0)) / minutes_per90
        self.xa_per90 = float(raw.get("xa", 0)) / minutes_per90
        self.progressive_carries_per90 = float(raw.get("progressive_carries", 0)) / minutes_per90
        self.pressures_per90 = float(raw.get("pressures", 0)) / minutes_per90

    def save_to_db(self, repository: PlayerRepository):
        """Saves this player and their stats directly to SQLite"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
              INSERT OR REPLACE INTO players
              (id, name, dob, nationality, position, club, tier, value, contract_expiry)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          """, (
            self.player_id, self.name, str(self.dob), self.nationality,
            self.position, self.current_club, self.league_tier,
            self.transfermarkt_value_gbp, str(self.contract_expiry)
        ))
        cursor.execute("""
              INSERT OR REPLACE INTO player_seasons
              (player_id, season, minutes, goals, assists, xg_per90, xa_per90)
              VALUES (?, ?, ?, ?, ?, ?, ?)
          """, (
            self.player_id, self.season, self.minutes_played,
            self.goals, self.assists, self.xg_per90, self.xa_per90
        ))
        conn.commit()
        conn.close()