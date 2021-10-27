from typing import Tuple

from constants.errors import ERR_SESSION_PLAYER_NON_HOST, ERR_SESSION_NON_EXISTENT, ERR_SESSION_PLAYER_NON_EXISTENT
from constants.exceptions import InvalidRequest
from model.abc_session import NonExistentPlayer
from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from service.handlers.abc_realtime_session_manager_handler import RealtimeSessionManagerHandler
from service.handlers.abc_session_player_message_handler import SessionPlayerMessageHandler
from service.session_managers.abc_session_manager import NonExistentSession

_KICK_REQUEST_PREFIX: str = "rk"


class KickRealtimeHandler(RealtimeSessionManagerHandler, SessionPlayerMessageHandler):

    def get_message_prefix(self) -> str:
        return _KICK_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received kick player {player_name} request from realtime session {session_name}. "
                           f"Source: {address}")

        try:
            session: RealtimeSession = self._get_session_manager().get(session_name)

            if not session.is_host(address):
                self._logger.debug(f"Requester address %{address} is not host, cannot accept kick request")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Requester is not host, cannot accept kick request")

            player_to_kick: RealtimePlayer = session.get_player(player_name)
            host_left: bool = session.is_host(player_to_kick.get_address())
            session.remove_player(player_to_kick.name)
            if host_left:
                self._get_session_manager().update_address_for(session_name, address)
            # No need to send messages to anybody
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player to kick {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
