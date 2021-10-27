from typing import Dict, Tuple

from model.one_shot_player import OneShotPlayer
from model.one_shot_session import OneShotSession
from service.session_managers.abc_session_manager import SessionManager

ONE_SHOT_TYPE: str = "one_shot"


class OneShotSessionManager(SessionManager[OneShotSession, OneShotPlayer]):

    def __init__(self):
        super().__init__()
        self._sessions_by_name: Dict[str, OneShotSession] = {}
        self._sessions_by_address: Dict[Tuple[str, int], OneShotSession] = {}

    def get_type(self) -> str:
        return ONE_SHOT_TYPE

    def _get_sessions_by_name(self) -> Dict[str, OneShotSession]:
        return self._sessions_by_name

    def _get_sessions_by_address(self) -> Dict[Tuple[str, int], OneShotSession]:
        return self._sessions_by_address

    def _generate_session(self, name: str, max_players: int,
                          host: OneShotPlayer, password: str = None) -> OneShotSession:
        return OneShotSession(name, max_players, host, password)

