from abc import ABC
from typing import Dict

from service.schedulers.abc_session_manager_scheduler import SessionManagerScheduler
from service.session_managers.one_shot_session_manager import OneShotSessionManager
from service.session_managers.realtime_session_manager import RealtimeSessionManager


class RealtimeSessionManagerScheduler(SessionManagerScheduler[OneShotSessionManager], ABC):

    def __init__(self, args: Dict = None, auto_schedule: bool = True):
        super().__init__(args, auto_schedule)
        self._session_manager = RealtimeSessionManager()

    def _get_session_manager(self) -> RealtimeSessionManager:
        return self._session_manager
