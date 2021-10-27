from typing import Tuple

from constants.errors import ERR_SESSION_SECRET_MISMATCH, ERR_SESSION_PLAYER_NON_EXISTENT, ERR_SESSION_NON_EXISTENT, \
    ERR_PLAYER_PORT_MISMATCH
from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from constants.exceptions import InvalidRequest
from service.handlers.abc_connect_message_handler import ConnectMessageHandler
from service.handlers.abc_realtime_session_manager_handler import RealtimeSessionManagerHandler
from service.session_managers.abc_session_manager import NonExistentSession

_HOST_NEW_PORT_PREFIX = "nc"
_CONNECT_REQUEST_PREFIX: str = "rc"  # TODO Duplicated constant
_OK_ANSWER: str = "ok"  # TODO Duplicated constant


class HostNewPortHandler(RealtimeSessionManagerHandler, ConnectMessageHandler):

    def get_message_prefix(self) -> str:
        return _HOST_NEW_PORT_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        # Here we use connect request parser but last field is considered the session secret instead of password
        session_name, player_name, session_secret = self.parse_connect_request(message, address)
        ip, port = address
        self._logger.debug(f"Received info about new port on host for realtime session {session_name} and player "
                           f"{player_name} Source: {address}")

        try:
            session: RealtimeSession = self._get_session_manager().get(session_name)
            if not session.secret_matches(session_secret):
                self._logger.debug(f"Session secret for session {session_name} does not match")
                self._send_message(address, ERR_SESSION_SECRET_MISMATCH)
                raise InvalidRequest(f"Session secret does not match")

            if not session.has_player(player_name):
                self._logger.debug(f"Player {player_name} is not in session {session_name}")
                self._send_message(session.host.get_address(), ERR_SESSION_PLAYER_NON_EXISTENT)
                raise InvalidRequest("Player to give new port to does not exist")

            player: RealtimePlayer = session.get_player(player_name)  # At this point this is guaranteed to exist
            if player.has_host_port() and player.host_port != port:
                self._logger.error(f"Host port assigned to player {player_name} does not match with the one sent")
                self._send_message(address, ERR_PLAYER_PORT_MISMATCH)
                raise InvalidRequest("Host sent a different port than the one already assigned to player")

            player.host_port = port
            self._send_message(session.host.get_address(), ":".join([_OK_ANSWER, player_name]))
            self._send_message(address, ":".join([_CONNECT_REQUEST_PREFIX] +
                                                 session.get_realtime_host_info_for(player_name)))
            self._logger.info(f"Created host port for player {player_name} in realtime session {session_name}")
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
