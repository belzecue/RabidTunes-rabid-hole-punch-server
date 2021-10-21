from typing import Tuple

from errors import ERR_SESSION_PLAYER_NON_EXISTENT, ERR_SESSION_NON_EXISTENT, ERR_SESSION_PLAYER_NON_HOST, \
    ERR_SESSION_PLAYER_KICKED_BY_HOST
from handlers.session_broadcaster_handler import SessionBroadcasterHandler
from handlers.session_player_handler import SessionPlayerHandler
from model import InvalidRequest, NonExistentPlayer, Session, Player
from session_manager import NonExistentSession

_KICK_REQUEST_PREFIX: str = "k"


class KickHandler(SessionPlayerHandler, SessionBroadcasterHandler):

    def get_message_prefix(self) -> str:
        return _KICK_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received kick player {player_name} request from session {session_name}. "
                           f"Source: {address}")

        try:
            session: Session = self._session_manager.get(session_name)

            if not session.is_host(address):
                self._logger.debug(f"Requester address %{address} is not host, cannot accept kick request")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Requester is not host, cannot accept kick request")

            if session.has_started():
                self._logger.debug(f"Session {session_name} already started cannot kick now")
                raise InvalidRequest("Session already started cannot accept kick request")

            player_to_kick: Player = session.get_player(player_name)
            session.remove_player(player_to_kick.name)
            self._send_message(player_to_kick.get_address(), ERR_SESSION_PLAYER_KICKED_BY_HOST)

            if session.has_players():
                self._broadcast_session_info(session)
            else:
                self._session_manager.delete(session_name)
                self._logger.info(f"No more players in session {session_name}, deleted session")
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player to kick {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
