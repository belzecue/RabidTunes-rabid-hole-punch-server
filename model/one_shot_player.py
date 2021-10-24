from model.player import Player
from utils.time import current_time_millis, SECONDS_TO_MILLIS

_PLAYER_TIMEOUT_MILLIS: int = 5 * SECONDS_TO_MILLIS


class OneShotPlayer(Player):

    def is_timed_out(self) -> bool:
        return current_time_millis() - self._last_seen > _PLAYER_TIMEOUT_MILLIS

    def __str__(self):
        return f"OneShotPlayer({self.name}, {self.ip}, {self.port}, {self._last_seen})"
