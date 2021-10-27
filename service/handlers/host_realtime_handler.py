from string import ascii_uppercase, digits, ascii_lowercase
from typing import Tuple

from constants.errors import ERR_SESSION_PLAYER_NON_HOST
from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from model.abc_session import NonExistentPlayer
from constants.exceptions import InvalidRequest
from service.handlers.abc_host_message_handler import HostMessageHandler
from service.handlers.abc_realtime_session_manager_handler import RealtimeSessionManagerHandler
from service.session_managers.abc_session_manager import AddressAlreadyHasSession, NonExistentSession

_HOST_REALTIME_REQUEST_PREFIX: str = "rh"
_OK_ANSWER: str = "ok"  # TODO Duplicated constant
_REALTIME_SECRET_CHARSET: str = ascii_uppercase + ascii_lowercase + digits
_REALTIME_SECRET_LENGTH: int = 12


class HostRealtimeHandler(RealtimeSessionManagerHandler, HostMessageHandler):

    def get_message_prefix(self) -> str:
        return _HOST_REALTIME_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        player_name, max_players, password = self._parse_host_request(message, address)
        ip, port = address
        self._logger.debug(f"Received request from player {player_name} to host realtime session for max {max_players} "
                           f"players. Source: {address}")
        try:
            player: RealtimePlayer = RealtimePlayer(player_name, ip, port)
            session: RealtimeSession = self._get_session_manager().create(player, max_players, password)
            self._logger.info(f"Created realtime session {session.name} (max {max_players} players)")
            self._send_message(address, ":".join([_OK_ANSWER, session.name, session.get_realtime_secret()]))
        except AddressAlreadyHasSession:
            self._logger.debug(f"Source address {address} already has a session created")
            try:
                session: RealtimeSession = self._session_manager.get_by_address(address)
                session.get_player(player_name).update_last_seen()
                self._logger.debug(f"Sending already created session {session.name} info")
                self._send_message(address, ":".join([_OK_ANSWER, session.name, session.get_realtime_secret()]))
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
