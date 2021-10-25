from typing import List

from constants.errors import ERR_SESSION_TIMEOUT
from model.one_shot_session import OneShotSession
from service.schedulers.message_sender_scheduler import MessageSenderScheduler
from service.schedulers.one_shot_session_manager_scheduler import OneShotSessionManagerScheduler
from utils.time import MINUTES_TO_SECONDS

_SCHEDULED_SESSION_CLEANUP_SECONDS: float = 5 * MINUTES_TO_SECONDS


class OneShotSessionCleanupScheduler(MessageSenderScheduler, OneShotSessionManagerScheduler):

    def get_seconds_for_next_execution(self) -> float:
        return _SCHEDULED_SESSION_CLEANUP_SECONDS

    def run(self):
        all_sessions: List[OneShotSession] = list(self._get_session_manager().get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting session cleanup")

        for session in all_sessions:
            if session.is_timed_out():
                self._session_manager.delete(session.name)
                for player in session.get_players():
                    self._send_message(player.get_address(), ERR_SESSION_TIMEOUT, 3)
                self._logger.info(f"Session {session.name} deleted because it timed out")
