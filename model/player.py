from abc import ABC, abstractmethod
from typing import Tuple

from utils.time import current_time_millis


class Player(ABC):

    def __init__(self, name: str, ip: str, port: int):
        self.name = name
        self.ip = ip
        self.port = port
        self._last_seen = current_time_millis()

    def get_address(self) -> Tuple[str, int]:
        return self.ip, self.port

    def update_last_seen(self):
        self._last_seen = current_time_millis()

    @abstractmethod
    def is_timed_out(self) -> bool:
        raise NotImplementedError

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name and self.ip == other.ip and self.port == other.port

    def __ne__(self, other):
        return not self.__eq__(other)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError
