from string import ascii_uppercase, digits, ascii_lowercase
from typing import Dict, Tuple

from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from service.session_managers.abc_session_manager import SessionManager
from utils.uuid import get_random_string

REALTIME_TYPE: str = "realtime"

_REALTIME_SECRET_CHARSET: str = ascii_uppercase + ascii_lowercase + digits
_REALTIME_SECRET_LENGTH: int = 12


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
        # This secret will be sent to host and will be used to identify them in order to know new ports they open
        secret: str = get_random_string(_REALTIME_SECRET_CHARSET, _REALTIME_SECRET_LENGTH)
        session: RealtimeSession = RealtimeSession(name, max_players, host, secret, password)
        return session

