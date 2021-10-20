import re
from typing import Tuple, Optional

from errors import ERR_INVALID_PLAYER_NAME, ERR_INVALID_SESSION_PASSWORD, ERR_REQUEST_INVALID, \
    ERR_SESSION_PASSWORD_MISMATCH, ERR_SESSION_PLAYER_NAME_IN_USE, ERR_SESSION_FULL, ERR_SESSION_NON_EXISTENT
from handlers.request_handler import RequestHandler
from model import InvalidRequest, Session, Player, IgnoredRequest
from session_manager import NonExistentSession

PLAYER_NAME_REGEX = "[A-Za-z0-9]{1,12}"
SESSION_PASS_REGEX = "[A-Za-z0-9]{1,12}"

_CONNECT_REQUEST_PREFIX: str = "c"
_INFO_PREFIX: str = "i"


class ConnectHandler(RequestHandler):

    def get_message_prefix(self) -> str:
        return _CONNECT_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name, session_password = self.parse_connect_request(message, address)
        ip, port = address
        self._logger.debug("Received connect request from player %s to session %s. Source: %s:%s",
                           player_name, session_name, ip, port)

        try:
            session: Session = self._session_manager.get(session_name)
            if not session.password_matches(session_password):
                self._logger.debug("Session password for session %s does not match", session_name)
                self.send_message(address, ERR_SESSION_PASSWORD_MISMATCH)
                raise InvalidRequest(f"Session password for session {session_name} does not match")

            if session.has_player(player_name):
                self._logger.debug("Player %s is already in session %s", player_name, session_name)
                player: Player = session.get_player(player_name)
                if player.get_address() != address:
                    self._logger.debug("Session %s already has a player with the exact same name (%s) coming from "
                                       "a different ip and port", session_name, player_name)
                    self.send_message(address, ERR_SESSION_PLAYER_NAME_IN_USE)
                    raise InvalidRequest("Session already has a player with the exact same name coming from a "
                                         "different ip and port")
                self.send_message(address, ":".join([_INFO_PREFIX] + session.get_player_names()))
                player.update_last_seen()
                raise IgnoredRequest

            if session.is_full():
                self._logger.debug("Session %s is full", session_name)
                self.send_message(address, ERR_SESSION_FULL)
                raise InvalidRequest(f"Session is full")

            session.add_player(Player(player_name, ip, port))
            self._logger.info("Connected player %s to session %s", player_name, session_name)
            self._broadcast_session_info(session)

        except NonExistentSession:
            self._logger.debug("Session %s does not exist", session_name)
            self.send_message(address, ERR_SESSION_NON_EXISTENT)

    def parse_connect_request(self, connect_request: str, address: Tuple[str, int]) -> Tuple[str, str, Optional[str]]:
        split = connect_request.split(":")
        if len(split) >= 2 or len(split) <= 3:
            session_name: str = split[0]  # TODO Verify session name integrity regex

            player_name: str = split[1]
            if not re.search(PLAYER_NAME_REGEX, player_name):
                self.send_message(address, ERR_INVALID_PLAYER_NAME)
                raise InvalidRequest(f"Invalid player name {player_name}")

            password: Optional[str] = None
            if len(split) == 3:
                password = split[2]
                if not re.search(SESSION_PASS_REGEX, password):
                    self.send_message(address, ERR_INVALID_SESSION_PASSWORD)
                    raise InvalidRequest("Invalid session password")

            return session_name, player_name, password
        else:
            self.send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid connect message received {connect_request}")

    def _broadcast_session_info(self, session: Session):
        for player in session.players_array:
            self.send_message((player.ip, player.port), ":".join([_INFO_PREFIX] + session.get_player_names()))
