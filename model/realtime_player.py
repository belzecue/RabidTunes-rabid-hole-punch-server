from typing import Optional

from model.abc_player import Player


class RealtimePlayer(Player):

    def __init__(self, name: str, ip: str, port: int, host_port: Optional[int] = None):
        super().__init__(name, ip, port)
        self.host_port: Optional[int] = host_port

    def has_host_port(self) -> bool:
        return self.host_port is not None

    def is_confirmed(self):
        return self.host_port is not None

    def is_timed_out(self) -> bool:
        return False  # TODO

    def __str__(self):
        return f"RealtimePlayer({self.name}, {self.ip}, {self.port}, {self._last_seen})"
