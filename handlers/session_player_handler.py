import re
from abc import ABC
from typing import Tuple

from errors import ERR_REQUEST_INVALID, ERR_INVALID_SESSION_NAME, ERR_INVALID_PLAYER_NAME
from handlers.request_handler import RequestHandler
from model import InvalidRequest
from regexes import SESSION_NAME_REGEX, PLAYER_NAME_REGEX


class SessionPlayerHandler(RequestHandler, ABC):
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
            self._send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid session/player message received {message}")

