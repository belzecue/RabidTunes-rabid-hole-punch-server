from typing import List

from constants.errors import ERR_SESSION_TIMEOUT
from model.realtime_session import RealtimeSession
from service.schedulers.abc_message_sender_scheduler import MessageSenderScheduler
from service.schedulers.abc_realtime_session_manager_scheduler import RealtimeSessionManagerScheduler
from utils.time import HOURS_TO_SECONDS

_SCHEDULED_SESSION_CLEANUP_SECONDS: float = 1 * HOURS_TO_SECONDS


class RealtimeSessionCleanupScheduler(MessageSenderScheduler, RealtimeSessionManagerScheduler):

    def get_seconds_for_next_execution(self) -> float:
        return _SCHEDULED_SESSION_CLEANUP_SECONDS

    def run(self):
        all_sessions: List[RealtimeSession] = list(self._get_session_manager().get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting realtime session cleanup")

        for session in all_sessions:
            if session.is_timed_out():
                self._session_manager.delete(session.name)
                for player in session.get_players():
                    self._send_message(player.get_address(), ERR_SESSION_TIMEOUT, 3)
                self._logger.info(f"Realtime session {session.name} deleted because it timed out")
