from typing import Dict, List

from model.realtime_player import RealtimePlayer
from model.session import Session
from utils.time import DAYS_TO_MILLIS, current_time_millis

_SESSION_TIMEOUT_MILLIS: int = 1 * DAYS_TO_MILLIS


class RealtimeSession(Session[RealtimePlayer]):

    def __init__(self, name: str, max_players: int, host: RealtimePlayer, secret: str, password: str = None):
        super().__init__(name, max_players, host, password)
        self._realtime_secret: str = secret
        self._realtime_player_host_ports: Dict[str, int] = {}

    def is_timed_out(self) -> bool:
        return current_time_millis() - self._created_at > _SESSION_TIMEOUT_MILLIS

    def get_realtime_host_info_for(self, player_name: str) -> List[str]:
        """
        If host has created a port for player_name this method will return [hostIP, hostPortForPlayerName]
        Otherwise it will return a single element list containing ["wait"]
        """
        if player_name in self._realtime_player_host_ports.keys():
            return [self.host.ip, str(self._realtime_player_host_ports[player_name])]
        else:
            return ['wait']

    def get_realtime_secret(self) -> str:
        return self._realtime_secret

    def __str__(self):
        return f"RealtimeSession({self.name}, {self._max_players}, {self.host}, {self._players}, {self._created_at})"

