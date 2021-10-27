from typing import Optional

from model.abc_player import Player
from utils.time import current_time_millis, SECONDS_TO_MILLIS

_HOST_PLAYER_TIMEOUT_MILLIS: int = 10 * SECONDS_TO_MILLIS
_CLIENT_PLAYER_TIMEOUT_MILLIS: int = 5 * SECONDS_TO_MILLIS


class RealtimePlayer(Player):

    def __init__(self, name: str, ip: str, port: int, host_port: Optional[int] = None):
        super().__init__(name, ip, port)
        self.host_port: Optional[int] = host_port  # If this player is host, set this number to negative

    def has_host_port(self) -> bool:
        return self.host_port is not None and self.host_port >= 0

    def is_host(self):
        return self.host_port is not None and self.host_port < 0

    def is_timed_out(self) -> bool:
        if self.is_host():
            return current_time_millis() - self._last_seen > _HOST_PLAYER_TIMEOUT_MILLIS
        else:
            if self.has_host_port():
                # Players with host port communicate directly with host and we won't be receiving messages from them
                # If they disconnect or time out it is host responsibility to kick them from room, but we won't mark
                # them as timed out
                return False
            else:
                # If host port hasn't been confirmed yet, this player can still timeout
                return current_time_millis() - self._last_seen > _CLIENT_PLAYER_TIMEOUT_MILLIS

    def __str__(self):
        return f"RealtimePlayer({self.name}, {self.ip}, {self.port}, {self._last_seen})"
