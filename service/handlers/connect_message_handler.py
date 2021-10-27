import re
from abc import ABC
from typing import Tuple, Optional

from constants.errors import ERR_INVALID_REQUEST, ERR_INVALID_SESSION_PASSWORD, ERR_INVALID_PLAYER_NAME, \
    ERR_INVALID_SESSION_NAME
from constants.regexes import SESSION_PASS_REGEX, PLAYER_NAME_REGEX, SESSION_NAME_REGEX
from constants.exceptions import InvalidRequest
from service.handlers.request_handler import RequestHandler


class ConnectMessageHandler(RequestHandler, ABC):

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
            self._send_message(address, ERR_INVALID_REQUEST)
            raise InvalidRequest(f"Invalid connect message received {connect_request}")