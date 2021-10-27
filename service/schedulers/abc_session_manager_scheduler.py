from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from service.schedulers.abc_scheduler import Scheduler
from service.session_managers.abc_session_manager import SessionManager

SM = TypeVar("SM", bound=SessionManager)


class SessionManagerScheduler(Scheduler, Generic[SM], ABC):

    @abstractmethod
    def _get_session_manager(self) -> SM:
        raise NotImplementedError
