from typing import Tuple

from constants.errors import ERR_SESSION_PASSWORD_MISMATCH, ERR_SESSION_PLAYER_NAME_IN_USE, ERR_SESSION_FULL, \
    ERR_SESSION_NON_EXISTENT
from model.one_shot_player import OneShotPlayer
from model.one_shot_session import OneShotSession
from server import InvalidRequest, IgnoredRequest
from service.handlers.connect_message_handler import ConnectMessageHandler
from service.handlers.one_shot_handler import OneShotHandler
from service.handlers.request_handler import INFO_PREFIX
from service.handlers.session_info_broadcaster_handler import SessionInfoBroadcasterHandler
from service.session_managers.session_manager import NonExistentSession

_CONNECT_REQUEST_PREFIX: str = "c"


class ConnectOneShotHandler(OneShotHandler, ConnectMessageHandler, SessionInfoBroadcasterHandler):

    def get_message_prefix(self) -> str:
        return _CONNECT_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name, session_password = self.parse_connect_request(message, address)
        ip, port = address
        self._logger.debug(f"Received connect request from player {player_name} to session {session_name}. "
                           f"Source: {address}")

        try:
            session: OneShotSession = self._get_session_manager().get(session_name)
            if not session.password_matches(session_password):
                self._logger.debug(f"Session password for session {session_name} does not match")
                self._send_message(address, ERR_SESSION_PASSWORD_MISMATCH)
                raise InvalidRequest(f"Session password does not match")

            if session.has_player(player_name):
                self._logger.debug(f"Player {player_name} is already in session {session_name}")
                player: OneShotPlayer = session.get_player(player_name)

                if player.get_address() != address:
                    self._logger.debug(f"Session {session_name} already has a player with the exact same name "
                                       f"({player_name}) coming from a different ip and port")
                    self._send_message(address, ERR_SESSION_PLAYER_NAME_IN_USE)
                    raise InvalidRequest("Session already has a player with the exact same name coming from a "
                                         "different ip and port")

                if session.is_realtime():
                    self._send_message(address, ":".join([_CONNECT_REQUEST_PREFIX] +
                                                         session.get_realtime_host_info_for(player_name)))
                else:
                    self._send_message(address, ":".join([INFO_PREFIX] + session.get_player_names()))
                player.update_last_seen()
                raise IgnoredRequest

            if session.is_full():
                self._logger.debug(f"Session {session_name} is full")
                self._send_message(address, ERR_SESSION_FULL)
                raise InvalidRequest("Session is full")

            session.add_player(OneShotPlayer(player_name, ip, port))
            self._logger.info(f"Connected player {player_name} to session {session_name}")
            self._broadcast_session_info(session)
            """
            if session.is_realtime():
                self._send_message(address, ":".join([_CONNECT_REQUEST_PREFIX] +
                                                     session.get_realtime_host_info_for(player_name)))
                self._send_message(session.host.get_address(), ":".join([_CONNECT_REQUEST_PREFIX, player_name,
                                                                         ip, port]), 5)
            else:
            """

        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
