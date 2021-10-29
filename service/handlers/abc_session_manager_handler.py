from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from service.handlers.abc_request_handler import RequestHandler
from service.session_managers.abc_session_manager import SessionManager

SM = TypeVar("SM", bound=SessionManager)


class SessionManagerHandler(RequestHandler, Generic[SM], ABC):

    @abstractmethod
    def _get_session_manager(self) -> SM:
        raise NotImplementedError