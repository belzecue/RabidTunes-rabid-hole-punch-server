import re
from abc import ABC
from typing import Tuple

from constants.errors import ERR_INVALID_REQUEST, ERR_INVALID_SESSION_NAME, ERR_INVALID_PLAYER_NAME
from server import InvalidRequest
from service.handlers.request_handler import RequestHandler
from constants.regexes import SESSION_NAME_REGEX, PLAYER_NAME_REGEX


class SessionPlayerMessageHandler(RequestHandler, ABC):

    def _parse_session_player_message_from(self, message: str, address: Tuple[str, int]) -> Tuple[str, str]:
        split = message.split(":")
        if len(split) == 2:
            session_name: str = split[0]
            if not re.search(SESSION_NAME_REGEX, session_name):
                self._send_message(address, ERR_INVALID_SESSION_NAME)
                raise InvalidRequest("Invalid session name")

            player_name: str = split[1]
            if not re.search(PLAYER_NAME_REGEX, player_name):
                self._send_message(address, ERR_INVALID_PLAYER_NAME)
                raise InvalidRequest("Invalid player name")

            return session_name, player_name
        else:
            self._send_message(address, ERR_INVALID_REQUEST)
            raise InvalidRequest(f"Invalid session/player message received {message}")

