from typing import Tuple

from constants.errors import ERR_SESSION_PASSWORD_MISMATCH, ERR_SESSION_PLAYER_NAME_IN_USE, ERR_SESSION_FULL, \
    ERR_SESSION_NON_EXISTENT
from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from constants.exceptions import InvalidRequest, IgnoredRequest
from service.handlers.abc_realtime_connect_message_handler import RealtimeConnectMessageHandler, \
    _REALTIME_CONNECT_REQUEST_PREFIX
from service.handlers.abc_realtime_session_manager_handler import RealtimeSessionManagerHandler
from service.session_managers.abc_session_manager import NonExistentSession

_NEW_CONNECTION_TO_HOST_PREFIX: str = "nc"


class ConnectRealtimeHandler(RealtimeSessionManagerHandler, RealtimeConnectMessageHandler):

    def get_message_prefix(self) -> str:
        return _REALTIME_CONNECT_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name, session_password = self.parse_connect_request(message, address)
        ip, port = address
        self._logger.debug(f"Received realtime connect request from player {player_name} to session {session_name}. "
                           f"Source: {address}")

        try:
            session: RealtimeSession = self._get_session_manager().get(session_name)
            if not session.password_matches(session_password):
                self._logger.debug(f"Session password for session {session_name} does not match")
                self._send_message(address, ERR_SESSION_PASSWORD_MISMATCH)
                raise InvalidRequest(f"Session password does not match")

            if session.has_player(player_name):
                self._logger.debug(f"Player {player_name} is already in session {session_name}")
                player: RealtimePlayer = session.get_player(player_name)

                if player.get_address() != address:
                    self._logger.debug(f"Session {session_name} already has a player with the exact same name "
                                       f"({player_name}) coming from a different ip and port")
                    self._send_message(address, ERR_SESSION_PLAYER_NAME_IN_USE)
                    raise InvalidRequest("Session already has a player with the exact same name coming from a "
                                         "different ip and port")

                self._send_message(address, ":".join([_CONNECT_REQUEST_PREFIX] +
                                                     session.get_realtime_host_info_for(player_name)))
                if not player.has_host_port():
                    self._send_message(session.host.get_address(), ":".join([_NEW_CONNECTION_TO_HOST_PREFIX,
                                                                             player_name, ip, str(port)]))
                raise IgnoredRequest

            if session.is_full():
                self._logger.debug(f"Session {session_name} is full")
                self._send_message(address, ERR_SESSION_FULL)
                raise InvalidRequest("Session is full")

            session.add_player(RealtimePlayer(player_name, ip, port))
            self._send_message(address, ":".join([_CONNECT_REQUEST_PREFIX] +
                                                 session.get_realtime_host_info_for(player_name)))
            self._send_message(session.host.get_address(), ":".join([_NEW_CONNECTION_TO_HOST_PREFIX,
                                                                     player_name, ip, str(port)]))
            self._logger.info(f"Connected player {player_name} to realtime session {session_name}")
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
