import re
from typing import Tuple, Optional

from errors import ERR_INVALID_PLAYER_NAME, ERR_INVALID_SESSION_PASSWORD, ERR_REQUEST_INVALID, \
    ERR_SESSION_PASSWORD_MISMATCH, ERR_SESSION_PLAYER_NAME_IN_USE, ERR_SESSION_FULL, ERR_SESSION_NON_EXISTENT, \
    ERR_INVALID_SESSION_NAME
from handlers.request_handler import INFO_PREFIX
from handlers.session_broadcaster_handler import SessionBroadcasterHandler
from model import InvalidRequest, Session, Player, IgnoredRequest
from regexes import SESSION_PASS_REGEX, PLAYER_NAME_REGEX, SESSION_NAME_REGEX
from session_manager import NonExistentSession

_CONNECT_REQUEST_PREFIX: str = "c"


class ConnectHandler(SessionBroadcasterHandler):

    def get_message_prefix(self) -> str:
        return _CONNECT_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name, session_password = self.parse_connect_request(message, address)
        ip, port = address
        self._logger.debug(f"Received connect request from player {player_name} to session {session_name}. "
                           f"Source: {address}")

        try:
            session: Session = self._session_manager.get(session_name)
            if not session.password_matches(session_password):
                self._logger.debug(f"Session password for session {session_name} does not match")
                self._send_message(address, ERR_SESSION_PASSWORD_MISMATCH)
                raise InvalidRequest(f"Session password does not match")

            if session.has_player(player_name):
                self._logger.debug(f"Player {player_name} is already in session {session_name}")
                player: Player = session.get_player(player_name)

                if player.get_address() != address:
                    self._logger.debug(f"Session {session_name} already has a player with the exact same name "
                                       f"({player_name}) coming from a different ip and port")
                    self._send_message(address, ERR_SESSION_PLAYER_NAME_IN_USE)
                    raise InvalidRequest("Session already has a player with the exact same name coming from a "
                                         "different ip and port")

                self._send_message(address, ":".join([INFO_PREFIX] + session.get_player_names()))
                player.update_last_seen()
                raise IgnoredRequest

            if session.is_full():
                self._logger.debug(f"Session {session_name} is full")
                self._send_message(address, ERR_SESSION_FULL)
                raise InvalidRequest("Session is full")

            session.add_player(Player(player_name, ip, port))
            self._logger.info(f"Connected player {player_name} to session {session_name}")
            self._broadcast_session_info(session)

        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)

    def parse_connect_request(self, connect_request: str, address: Tuple[str, int]) -> Tuple[str, str, Optional[str]]:
        split = connect_request.split(":")
        if len(split) >= 2 or len(split) <= 3:
            session_name: str = split[0]
            if not re.search(SESSION_NAME_REGEX, session_name):
                self._send_message(address, ERR_INVALID_SESSION_NAME)
                raise InvalidRequest("Invalid session name")

            player_name: str = split[1]
            if not re.search(PLAYER_NAME_REGEX, player_name):
                self._send_message(address, ERR_INVALID_PLAYER_NAME)
                raise InvalidRequest("Invalid player name")

            password: Optional[str] = None
            if len(split) == 3:
                password = split[2]
                if not re.search(SESSION_PASS_REGEX, password):
                    self._send_message(address, ERR_INVALID_SESSION_PASSWORD)
                    raise InvalidRequest("Invalid session password")

            return session_name, player_name, password
        else:
            self._send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid connect message received {connect_request}")
