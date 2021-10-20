import re
from typing import Tuple, Optional

from errors import ERR_REQUEST_INVALID, ERR_INVALID_PLAYER_NAME, ERR_INVALID_SESSION_PASSWORD, ERR_INVALID_MAX_PLAYERS, \
    ERR_SESSION_PLAYER_NON_EXISTENT
from handlers.request_handler import RequestHandler
from model import InvalidRequest, Session, Player, NonExistentPlayer
from session_manager import AddressAlreadyHasSession, NonExistentSession

PLAYER_NAME_REGEX = "[A-Za-z0-9]{1,12}"
MAX_PLAYERS_REGEX = "([2-9]|1[0-2])"
SESSION_PASS_REGEX = "[A-Za-z0-9]{1,12}"

_HOST_REQUEST_PREFIX: str = "h"
_INFO_PREFIX: str = "i"


class HostHandler(RequestHandler):

    def get_message_prefix(self) -> str:
        return _HOST_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        player_name, max_players, password = self._parse_host_request(message, address)
        ip, port = address
        self._logger.debug("Received request from player %s to host session for max %s players. Source: %s:%s",
                           player_name, max_players, ip, port)
        try:
            session: Session = self._session_manager.create(Player(player_name, ip, port), max_players, password)
            self._logger.info("Created session %s (max %s players)", session.name, max_players)
            self.send_message(address, ":".join([_INFO_PREFIX] + session.get_player_names()))
        except AddressAlreadyHasSession:
            try:
                session: Session = self._session_manager.get_by_address(address)
                session.get_player(player_name).update_last_seen()
                self.send_message(address, ":".join([_INFO_PREFIX] + session.get_player_names()))
            except NonExistentPlayer as e:
                self._logger.debug("Player %s does not exist in session for address %s", player_name, address)
                self.send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
                raise InvalidRequest(e)
            except NonExistentSession as e:
                self._logger.error("Inconsistent state, player already has session created but session manager "
                                   "says no session for that address %s", address)
                raise e

    def _parse_host_request(self, host_request: str, address: Tuple[str, int]) -> Tuple[str, int, Optional[str]]:
        split = host_request.split(":")
        if len(split) >= 2 or len(split) <= 3:
            player_name: str = split[0]
            if not re.search(PLAYER_NAME_REGEX, player_name):
                self.send_message(address, ERR_INVALID_PLAYER_NAME)
                raise InvalidRequest(f"Invalid player name {player_name}")

            max_players_str: str = split[1]
            if not re.search(MAX_PLAYERS_REGEX, max_players_str):
                self.send_message(address, ERR_INVALID_MAX_PLAYERS)
                raise InvalidRequest(f"Invalid max players {max_players_str}")
            max_players: int = int(max_players_str)

            password: Optional[str] = None
            if len(split) == 3:
                password = split[2]
                if not re.search(SESSION_PASS_REGEX, password):
                    self.send_message(address, ERR_INVALID_SESSION_PASSWORD)
                    raise InvalidRequest("Invalid session password")

            return player_name, max_players, password
        else:
            self.send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid host message received {host_request}")
