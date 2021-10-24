from typing import Dict, List, Callable

from twisted.internet import reactor

from constants.errors import ERR_SESSION_TIMEOUT
from service.scheduleds.scheduled import Scheduled

_SCHEDULED_SESSION_CLEANUP_SECONDS: float = 60 * 5  # 5 min
SEND_MESSAGE_ARG_NAME: str


class SessionCleanupScheduled(Scheduled):

    def __init__(self, args: Dict = None, auto_schedule: bool = True):
        super().__init__(args, auto_schedule)
        if SEND_MESSAGE_ARG_NAME not in self._args:
            raise Exception(f"Missing argument {SEND_MESSAGE_ARG_NAME} in SessionCleanupScheduled")
        self._send_message: Callable = args[SEND_MESSAGE_ARG_NAME]

    def get_seconds_for_next_execution(self) -> float:
        return _SCHEDULED_SESSION_CLEANUP_SECONDS

    def run(self):
        all_sessions: List[Session] = list(self._session_manager.get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting session cleanup")

        for session in all_sessions:
            if session.is_timed_out():
                self._session_manager.delete(session.name)
                for player in session.get_players():
                    self._send_message(player.get_address(), ERR_SESSION_TIMEOUT, 3)
                self._logger.info(f"Session {session.name} deleted because it timed out")
        reactor.callLater(_SCHEDULED_SESSION_CLEANUP_SECONDS, self._cleanup_sessions)
