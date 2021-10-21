"""
Data classes to facilitate operations by the server
"""

import time
from typing import List, Dict, Tuple, Optional

_PLAYER_TIMEOUT_MILLIS: int = 5 * 1000
_SESSION_TIMEOUT_MILLIS: int = 15 * 60 * 1000
REALTIME_SESSION_TIMEOUT_MSECS: int = 80 * 1000


class Player:

    def __init__(self, name: str, ip: str, port: int):
        self.name = name
        self.ip = ip
        self.port = port
        self._last_seen = current_time_millis()

    def get_address(self) -> Tuple[str, int]:
        return self.ip, self.port

    def update_last_seen(self):
        self._last_seen = current_time_millis()

    def is_timed_out(self) -> bool:
        return current_time_millis() - self._last_seen > _PLAYER_TIMEOUT_MILLIS

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"Player({self.name}, {self.ip}, {self.port}, {self._last_seen})"


class Session:

    def __init__(self, name: str, max_players: int, host: Player, password: str = None, secret: str = None):
        self.name: str = name
        self.host: Optional[Player] = host
        self._max_players: int = max_players
        self._password: Optional[str] = password
        self._players: Dict[str, Player] = {host.name: host}
        self._players_array: List[Player] = [host]
        self._created_at: int = current_time_millis()
        self._started_at: Optional[int] = None
        self.secret: str = secret
        self.realtime: bool = False

    def get_player(self, player_name: str) -> Player:
        player: Player = self._players.get(player_name)
        if not player:
            raise NonExistentPlayer
        return player

    def get_players(self) -> List[Player]:
        return self._players_array

    def get_player_names(self) -> List[str]:
        return [player.name for player in self._players_array]

    def get_players_addresses_except(self, current_player: Player) -> str:
        return ";".join([f"{player.name}:{player.ip}:{player.port}" for player in self._players_array
                         if player.name != current_player.name])

    def has_player(self, player_name: str) -> bool:
        return player_name in self._players.keys()

    def has_players(self) -> bool:
        return len(self._players_array) > 0

    def add_player(self, player: Player):
        if len(self._players_array) < self._max_players and player.name not in self._players:
            self._players_array.append(player)
            self._players[player.name] = player

    def remove_player(self, player_name: str):
        if self.has_player(player_name):
            del self._players[player_name]
            self._players_array = [player for player in self._players_array if player.name != player_name]
            if self._players_array:
                self.host = self._players_array[0]
            else:
                self.host = None

    def is_host(self, address: Tuple[str, int]) -> bool:
        ip, port = address
        return self.host.ip == ip and self.host.port == port

    def is_full(self) -> bool:
        return len(self._players_array) == self._max_players

    def password_matches(self, input_password: str) -> bool:
        if self._password is None:
            return True
        if input_password is None:
            return False
        return self._password == input_password

    def start(self):
        self._started_at = current_time_millis()

    def has_started(self) -> bool:
        return self._started_at is not None

    def is_timed_out(self) -> bool:
        if self.has_started():
            return False
        return current_time_millis() - self._created_at > _SESSION_TIMEOUT_MILLIS
        # TODO Realtime checks
        """
        if self.is_realtime():
            return current_time_millis() - self.host._last_seen > REALTIME_SESSION_TIMEOUT_MSECS
        else:
            return current_time_millis() - self._created_at > SESSION_TIMEOUT_MSECS
        """

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"Session({self.name}, {self._max_players}, {self.host}, {self._players}, {self._started_at})"


def current_time_millis():
    return int(time.time() * 1000)


class InvalidRequest(Exception):
    pass


class IgnoredRequest(Exception):
    pass


class SessionException(Exception):
    pass


class NonExistentPlayer(SessionException):
    pass
