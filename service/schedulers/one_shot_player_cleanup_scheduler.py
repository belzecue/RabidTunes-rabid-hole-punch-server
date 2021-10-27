from typing import List

from constants.errors import ERR_PLAYER_TIMEOUT
from model.one_shot_player import OneShotPlayer
from model.one_shot_session import OneShotSession
from service.schedulers.abc_message_sender_scheduler import MessageSenderScheduler
from service.schedulers.abc_one_shot_session_manager_scheduler import OneShotSessionManagerScheduler

_SCHEDULED_PLAYER_CLEANUP_SECONDS: float = 8


class OneShotPlayerCleanupScheduler(MessageSenderScheduler, OneShotSessionManagerScheduler):

    def get_seconds_for_next_execution(self) -> float:
        return _SCHEDULED_PLAYER_CLEANUP_SECONDS

    def run(self):
        all_sessions: List[OneShotSession] = list(self._session_manager.get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting player cleanup")

        for session in all_sessions:
            to_kick: List[OneShotPlayer] = [player for player in session.get_players() if player.is_timed_out()]
            for player in to_kick:
                session.remove_player(player.name)
                self._send_message(player.get_address(), ERR_PLAYER_TIMEOUT, 3)
                self._logger.info(f"Kicked player {player.name} from session {session.name} because it timed out")
            if not session.has_players():
                self._session_manager.delete(session.name)
                self._logger.info(f"No more players in session {session.name}, deleted session")
                continue
