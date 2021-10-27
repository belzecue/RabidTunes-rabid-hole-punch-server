from typing import Tuple

from constants.errors import ERR_SESSION_NON_EXISTENT, ERR_SESSION_PLAYER_NON_EXISTENT, ERR_SESSION_PLAYER_NON_HOST
from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from model.session import NonExistentPlayer
from constants.exceptions import InvalidRequest
from service.handlers.realtime_session_manager_handler import RealtimeSessionManagerHandler
from service.handlers.session_player_message_handler import SessionPlayerMessageHandler
from service.session_managers.session_manager import NonExistentSession

_PING_REQUEST_PREFIX: str = "rp"


class PingRealtimeHandler(RealtimeSessionManagerHandler, SessionPlayerMessageHandler):

    def get_message_prefix(self) -> str:
        return _PING_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received ping from player {player_name} from session {session_name}. "
                           f"Source: {address}")

        try:
            session: RealtimeSession = self._get_session_manager().get(session_name)
            player: RealtimePlayer = session.get_player(player_name)
            if not session.is_host(address):
                self._logger.debug(f"Address {address} is not host for realtime session {session.name}")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Address is not host for realtime session")

            if player.get_address() != address:
                self._logger.debug(f"Address {address} does not match player {player_name} "
                                   f"address {player.get_address()}")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Address does not match player address for ping")

            player.update_last_seen()
            self._send_message(address, "I DONT KNOW LOL")  # TODO
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
