from typing import Optional

from model.player import Player
from utils.time import current_time_millis


class RealtimePlayer(Player):

    def __init__(self, name: str, ip: str, port: int, host_port: Optional[int] = None):
        super().__init__(name, ip, port)
        self._host_port: Optional[int] = host_port

    def is_confirmed(self):
        return self._host_port is not None

    def is_timed_out(self) -> bool:
        if self.is_confirmed():


    def __str__(self):
        return f"RealtimePlayer({self.name}, {self.ip}, {self.port}, {self._last_seen})"
