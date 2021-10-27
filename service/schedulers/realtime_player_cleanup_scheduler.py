from typing import List

from constants.errors import ERR_PLAYER_TIMEOUT
from model.realtime_session import RealtimeSession
from service.schedulers.abc_message_sender_scheduler import MessageSenderScheduler
from service.schedulers.abc_realtime_session_manager_scheduler import RealtimeSessionManagerScheduler

_SCHEDULED_PLAYER_CLEANUP_SECONDS: float = 10


class RealtimePlayerCleanupScheduler(MessageSenderScheduler, RealtimeSessionManagerScheduler):

    def get_seconds_for_next_execution(self) -> float:
        return _SCHEDULED_PLAYER_CLEANUP_SECONDS

    def run(self):
        all_sessions: List[RealtimeSession] = list(self._session_manager.get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting realtime player cleanup")

        for session in all_sessions:
            if session.host.is_timed_out():
                self._send_message(session.host.get_address(), ERR_PLAYER_TIMEOUT, 3)
                self._logger.info(f"Host {session.host.name} from realtime session {session.name} timed out. "
                                  f"Deleting session")
                self._session_manager.delete(session.name)
