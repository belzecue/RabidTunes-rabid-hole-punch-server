import re
from abc import ABC
from typing import Tuple, Optional

from constants.errors import ERR_INVALID_PLAYER_NAME, ERR_INVALID_MAX_PLAYERS, ERR_INVALID_SESSION_PASSWORD, \
    ERR_INVALID_REQUEST
from constants.regexes import PLAYER_NAME_REGEX, MAX_PLAYERS_REGEX, SESSION_PASS_REGEX
from constants.exceptions import InvalidRequest
from service.handlers.abc_request_handler import RequestHandler


class HostMessageHandler(RequestHandler, ABC):

    def _parse_host_request(self, host_request: str, address: Tuple[str, int]) -> Tuple[str, int, Optional[str]]:
        split = host_request.split(":")
        if len(split) >= 2 or len(split) <= 3:
            player_name: str = split[0]
            if not re.search(PLAYER_NAME_REGEX, player_name):
                self._send_message(address, ERR_INVALID_PLAYER_NAME)
                raise InvalidRequest("Invalid player name")

            max_players_str: str = split[1]
            if not re.search(MAX_PLAYERS_REGEX, max_players_str):
                self._send_message(address, ERR_INVALID_MAX_PLAYERS)
                raise InvalidRequest("Invalid max players")
            max_players: int = int(max_players_str)

            password: Optional[str] = None
            if len(split) == 3:
                password = split[2]
                if not re.search(SESSION_PASS_REGEX, password):
                    self._send_message(address, ERR_INVALID_SESSION_PASSWORD)
                    raise InvalidRequest("Invalid session password")

            return player_name, max_players, password
        else:
            self._send_message(address, ERR_INVALID_REQUEST)
            raise InvalidRequest(f"Invalid host message received {host_request}")
