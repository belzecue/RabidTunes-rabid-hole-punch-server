from abc import ABC
from collections import Callable

from service.handlers.session_manager_handler import SessionManagerHandler
from service.session_managers.one_shot_session_manager import OneShotSessionManager


class OneShotSessionManagerHandler(SessionManagerHandler[OneShotSessionManager], ABC):

    def __init__(self, send_message_function: Callable):
        super().__init__(send_message_function)
        self._session_manager = OneShotSessionManager()

    def _get_session_manager(self) -> OneShotSessionManager:
        return self._session_manager
