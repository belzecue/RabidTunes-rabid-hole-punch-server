from typing import Tuple

from constants.errors import ERR_SESSION_PLAYER_NON_EXISTENT, ERR_SESSION_NON_EXISTENT, ERR_SESSION_PLAYER_NON_HOST, \
    ERR_SESSION_PLAYER_KICKED_BY_HOST
from model.one_shot_player import OneShotPlayer
from model.one_shot_session import OneShotSession
from model.session import NonExistentPlayer
from server import InvalidRequest
from service.handlers.one_shot_handler import OneShotHandler
from service.handlers.session_info_broadcaster_handler import SessionInfoBroadcasterHandler
from service.handlers.session_player_message_handler import SessionPlayerMessageHandler
from service.session_managers.session_manager import NonExistentSession

_KICK_REQUEST_PREFIX: str = "k"


class KickHandler(OneShotHandler, SessionPlayerMessageHandler, SessionInfoBroadcasterHandler):

    def get_message_prefix(self) -> str:
        return _KICK_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received kick player {player_name} request from session {session_name}. "
                           f"Source: {address}")

        try:
            session: OneShotSession = self._get_session_manager().get(session_name)

            if not session.is_host(address):
                self._logger.debug(f"Requester address %{address} is not host, cannot accept kick request")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Requester is not host, cannot accept kick request")

            if session.has_started():
                self._logger.debug(f"Session {session_name} already started cannot kick now")
                raise InvalidRequest("Session already started cannot accept kick request")

            player_to_kick: OneShotPlayer = session.get_player(player_name)
            session.remove_player(player_to_kick.name)
            self._send_message(player_to_kick.get_address(), ERR_SESSION_PLAYER_KICKED_BY_HOST)
            self._broadcast_session_info(session)
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player to kick {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
