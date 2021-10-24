from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple, TypeVar, Generic

from model.player import Player
from utils.time import current_time_millis

P = TypeVar("P", bound=Player)


class Session(ABC, Generic[P]):

    def __init__(self, name: str, max_players: int, host: P, password: str = None):
        self.name: str = name
        self.host: P = host
        self._max_players: int = max_players
        self._password: Optional[str] = password
        self._players: Dict[str, P] = {host.name: host}
        self._players_array: List[P] = [host]
        self._created_at: int = current_time_millis()

    def get_player(self, player_name: str) -> P:
        player: P = self._players.get(player_name)
        if not player:
            raise NonExistentPlayer
        return player

    def get_players(self) -> List[P]:
        return self._players_array

    def get_player_names(self) -> List[str]:
        return [player.name for player in self._players_array]

    def get_players_addresses_string_except(self, player: P) -> str:
        return ";".join([f"{array_player.name}:{array_player.ip}:{array_player.port}"
                         for array_player in self._players_array if array_player.name != player.name])

    def has_player(self, player_name: str) -> bool:
        return player_name in self._players.keys()

    def has_players(self) -> bool:
        return len(self._players_array) > 0

    def add_player(self, player: P):
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

    @abstractmethod
    def is_timed_out(self) -> bool:
        raise NotImplementedError

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class SessionException(Exception):
    pass


class NonExistentPlayer(SessionException):
    pass
