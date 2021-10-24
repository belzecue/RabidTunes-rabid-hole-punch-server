from typing import Tuple

from constants.errors import ERR_SESSION_PLAYER_NON_HOST
from model.one_shot_player import OneShotPlayer
from model.one_shot_session import OneShotSession
from model.session import NonExistentPlayer
from server import InvalidRequest
from service.handlers.host_message_handler import HostMessageHandler
from service.handlers.one_shot_handler import OneShotHandler
from service.handlers.request_handler import INFO_PREFIX
from service.session_managers.session_manager import AddressAlreadyHasSession, NonExistentSession

_HOST_REQUEST_PREFIX: str = "h"


class HostOneShotHandler(OneShotHandler, HostMessageHandler):

    def get_message_prefix(self) -> str:
        return _HOST_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        player_name, max_players, password = self._parse_host_request(message, address)
        ip, port = address
        self._logger.debug(f"Received request from player {player_name} to host session for max {max_players} players. "
                           f"Source: {address}")
        try:
            player: OneShotPlayer = OneShotPlayer(player_name, ip, port)
            session: OneShotSession = self._get_session_manager().create(player, max_players, password)
            self._logger.info(f"Created session {session.name} (max {max_players} players)")
            self._send_message(address, ":".join([INFO_PREFIX] + session.get_player_names()))
        except AddressAlreadyHasSession:
            self._logger.debug(f"Source address {address} already has a session created")
            try:
                session: OneShotSession = self._get_session_manager().get_by_address(address)
                session.get_player(player_name).update_last_seen()
                self._logger.debug(f"Sending already created session {session.name} info")
                self._send_message(address, ":".join([INFO_PREFIX] + session.get_player_names()))
            except NonExistentPlayer as e:
                self._logger.debug(f"Source address {address} wanted to create a new session but already has a "
                                   f"session created with a different player name {player_name}, "
                                   f"we will send them an error as the player name provided is not the one who created"
                                   f"the session")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest(e)
            except NonExistentSession as e:
                self._logger.error(f"Inconsistent state, player {player_name} already has a session created but "
                                   f"session manager says there is no session for that address {address}")
                raise e
