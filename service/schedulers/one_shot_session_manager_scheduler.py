from abc import ABC
from typing import Dict

from service.schedulers.session_manager_scheduler import SessionManagerScheduler
from service.session_managers.one_shot_session_manager import OneShotSessionManager


class OneShotSessionManagerScheduler(SessionManagerScheduler[OneShotSessionManager], ABC):

    def __init__(self, args: Dict = None, auto_schedule: bool = True):
        super().__init__(args, auto_schedule)
        self._session_manager = OneShotSessionManager()

    def _get_session_manager(self) -> OneShotSessionManager:
        return self._session_manager
