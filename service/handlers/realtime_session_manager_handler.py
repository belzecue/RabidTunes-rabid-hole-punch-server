from abc import ABC
from collections import Callable

from service.handlers.session_manager_handler import SessionManagerHandler
from service.session_managers.realtime_session_manager import RealtimeSessionManager


class RealtimeSessionManagerHandler(SessionManagerHandler[RealtimeSessionManager], ABC):

    def __init__(self, send_message_function: Callable):
        super().__init__(send_message_function)
        self._session_manager = RealtimeSessionManager()

    def _get_session_manager(self) -> RealtimeSessionManager:
        return self._session_manager
