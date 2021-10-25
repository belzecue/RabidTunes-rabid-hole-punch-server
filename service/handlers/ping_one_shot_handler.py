from typing import Tuple

from constants.errors import ERR_PLAYER_ADDRESS_MISMATCH, ERR_SESSION_PLAYER_NON_EXISTENT, \
    ERR_SESSION_NON_EXISTENT
from model.one_shot_player import OneShotPlayer
from model.one_shot_session import OneShotSession
from model.session import NonExistentPlayer
from server import InvalidRequest
from service.handlers.one_shot_session_manager_handler import OneShotSessionManagerHandler
from service.handlers.request_handler import INFO_PREFIX
from service.handlers.session_player_message_handler import SessionPlayerMessageHandler
from service.handlers.start_handler import START_REQUEST_PREFIX
from service.session_managers.session_manager import NonExistentSession

_PING_REQUEST_PREFIX: str = "p"


class PingOneShotHandler(OneShotSessionManagerHandler, SessionPlayerMessageHandler):

    def get_message_prefix(self) -> str:
        return _PING_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received ping from player {player_name} from session {session_name}. "
                           f"Source: {address}")

        try:
            session: OneShotSession = self._get_session_manager().get(session_name)
            player: OneShotPlayer = session.get_player(player_name)
            if player.get_address() != address:
                self._logger.debug(f"Address {address} does not match player {player_name} "
                                   f"address {player.get_address()}")
                self._send_message(address, ERR_PLAYER_ADDRESS_MISMATCH)
                raise InvalidRequest("Address does not match player address for ping")

            player.update_last_seen()
            if session.has_started():
                self._send_message(address,
                                   f"{START_REQUEST_PREFIX}"
                                   f":{player.port}"
                                   f":{session.get_players_addresses_string_except(player)}")
            else:
                self._send_message(address, ":".join([INFO_PREFIX] + session.get_player_names()))
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
