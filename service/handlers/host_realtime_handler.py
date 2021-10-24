from string import ascii_uppercase, digits, ascii_lowercase
from typing import Tuple

from constants.errors import ERR_SESSION_ALREADY_CREATED_FOR_ADDRESS, ERR_SESSION_PLAYER_NON_HOST
from model.realtime_player import RealtimePlayer
from model.realtime_session import RealtimeSession
from service.handlers.host_message_handler import HostMessageHandler
from service.handlers.realtime_handler import RealtimeHandler
from service.handlers.request_handler import INFO_PREFIX
from service.session_managers.session_manager import AddressAlreadyHasSession, NonExistentSession
from utils.uuid import get_random_string

_HOST_REALTIME_REQUEST_PREFIX: str = "hr"
_REALTIME_SECRET_CHARSET: str = ascii_uppercase + ascii_lowercase + digits
_REALTIME_SECRET_LENGTH: int = 12


class HostRealtimeHandler(RealtimeHandler, HostMessageHandler):

    def get_message_prefix(self) -> str:
        return _HOST_REALTIME_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        player_name, max_players, password = self._parse_host_request(message, address)
        ip, port = address
        self._logger.debug(f"Received request from player {player_name} to host realtime session for max {max_players} "
                           f"players. Source: {address}")
        try:
            realtime_secret: str = get_random_string(_REALTIME_SECRET_CHARSET, _REALTIME_SECRET_LENGTH)
            player: RealtimePlayer = RealtimePlayer(player_name, ip, port, realtime_secret)
            session: RealtimeSession = self._get_session_manager().create(player, max_players, password)
            self._logger.info(f"Created realtime session {session.name} (max {max_players} players)")
            self._send_message(address, ":".join([INFO_PREFIX, session.name, realtime_secret]))
        except AddressAlreadyHasSession:
            self._logger.debug(f"Source address {address} already has a session created")
            try:
                session: Session = self._session_manager.get_by_address(address)
                if not session.is_realtime():
                    self._logger.debug(f"Source address {address} wanted to create a new realtime session but already "
                                       f"has a non realtime session created")
                    self._send_message(address, ERR_SESSION_ALREADY_CREATED_FOR_ADDRESS)
                    raise InvalidRequest("Source address wanted to create a new realtime session but has already "
                                         "a non realtime session created")
                session.get_player(player_name).update_last_seen()
                self._logger.debug(f"Sending already created session {session.name} info")
                self._send_message(address, ":".join([INFO_PREFIX, session.name, session.get_realtime_secret()]))
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
