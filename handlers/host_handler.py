import re
from typing import Tuple, Optional

from errors import ERR_REQUEST_INVALID, ERR_INVALID_PLAYER_NAME, ERR_INVALID_SESSION_PASSWORD, \
    ERR_INVALID_MAX_PLAYERS, ERR_SESSION_PLAYER_NON_HOST
from handlers.request_handler import RequestHandler, INFO_PREFIX
from model import InvalidRequest, Session, Player, NonExistentPlayer
from regexes import MAX_PLAYERS_REGEX, PLAYER_NAME_REGEX, SESSION_PASS_REGEX
from session_manager import AddressAlreadyHasSession, NonExistentSession

_HOST_REQUEST_PREFIX: str = "h"


class HostHandler(RequestHandler):

    def get_message_prefix(self) -> str:
        return _HOST_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        player_name, max_players, password = self._parse_host_request(message, address)
        ip, port = address
        self._logger.debug(f"Received request from player {player_name} to host session for max {max_players} players. "
                           f"Source: {address}")
        try:
            session: Session = self._session_manager.create(Player(player_name, ip, port), max_players, password)
            self._logger.info(f"Created session {session.name} (max {max_players} players)")
            self._send_message(address, ":".join([INFO_PREFIX] + session.get_player_names()))
        except AddressAlreadyHasSession:
            self._logger.debug(f"Source address {address} already has a session created")
            try:
                session: Session = self._session_manager.get_by_address(address)
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
            self._send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid host message received {host_request}")
