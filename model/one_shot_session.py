from typing import Optional

from model.one_shot_player import OneShotPlayer
from model.session import Session
from utils.time import current_time_millis, MINUTES_TO_MILLIS

_SESSION_TIMEOUT_MILLIS: int = 30 * MINUTES_TO_MILLIS
_SESSION_STARTED_TIMEOUT_MILLIS: int = 5 * MINUTES_TO_MILLIS


class OneShotSession(Session[OneShotPlayer]):

    def __init__(self, name: str, max_players: int, host: OneShotPlayer, password: str = None):
        super().__init__(name, max_players, host, password)
        self._started_at: Optional[int] = None

    def is_timed_out(self) -> bool:
        if self.has_started():
            return current_time_millis() - self._started_at > _SESSION_STARTED_TIMEOUT_MILLIS
        return current_time_millis() - self._created_at > _SESSION_TIMEOUT_MILLIS

    def start(self):
        self._started_at = current_time_millis()

    def has_started(self) -> bool:
        return self._started_at is not None

    def __str__(self):
        return f"OneShotSession({self.name}, {self._max_players}, {self.host}, {self._players}, {self._created_at})"
