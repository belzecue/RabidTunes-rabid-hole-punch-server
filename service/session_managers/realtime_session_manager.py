from typing import Dict, Tuple

from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from service.session_managers.session_manager import SessionManager

REALTIME_TYPE = "realtime"


class RealtimeSessionManager(SessionManager[RealtimeSession, RealtimePlayer]):

    def __init__(self):
        super().__init__()
        self._sessions_by_name: Dict[str, RealtimeSession] = {}
        self._sessions_by_address: Dict[Tuple[str, int], RealtimeSession] = {}

    def get_type(self) -> str:
        return REALTIME_TYPE

    def _get_sessions_by_name(self) -> Dict[str, RealtimeSession]:
        return self._sessions_by_name

    def _get_sessions_by_address(self) -> Dict[Tuple[str, int], RealtimeSession]:
        return self._sessions_by_address

    def _generate_session(self, name: str, max_players: int,
                          host: RealtimePlayer, password: str = None) -> RealtimeSession:
        session: RealtimeSession = RealtimeSession(name, max_players, host, password)
        session.set_realtime_secret(secret)  # TODO
        return session

