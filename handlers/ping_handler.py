from typing import Tuple

from errors import ERR_REQUEST_INVALID, ERR_PLAYER_ADDRESS_MISMATCH, ERR_SESSION_PLAYER_NON_EXISTENT, \
    ERR_SESSION_NON_EXISTENT
from handlers.request_handler import RequestHandler
from model import InvalidRequest, Session, Player, NonExistentPlayer
from session_manager import NonExistentSession

_PING_REQUEST_PREFIX: str = "p"
_INFO_PREFIX: str = "i"
_START_PREFIX: str = "s"


class PingHandler(RequestHandler):

    def get_message_prefix(self) -> str:
        return _PING_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_ping_message_from(message, address)
        ip, port = address
        self._logger.debug("Received ping from player %s from session %s. Source: %s:%s",
                           player_name, session_name, ip, port)

        try:
            session: Session = self._session_manager.get(session_name)
            player: Player = session.get_player(player_name)
            if player.get_address() != address:
                self._logger.debug("Address %s does not match player %s's address %s",
                                   address, player_name, player.get_address())
                self.send_message(address, ERR_PLAYER_ADDRESS_MISMATCH)
                raise InvalidRequest("Address does not match player address for ping")

            player.update_last_seen()
            if session.has_started():
                pass  # TODO Send players ip and addresses
                # self.send_message(address, f"s:{player.port}:{session.get_session_players_addresses_except(player)}")
            else:
                self.send_message(address, ":".join([_INFO_PREFIX] + session.get_player_names()))
        except NonExistentSession:
            self._logger.debug("Session %s does not exist", session_name)
            self.send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug("Player %s does not exist in session %s", player_name, session_name)
            self.send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)

    def _parse_ping_message_from(self, message: str, address: Tuple[str, int]) -> Tuple[str, str]:
        split = message.split(":")
        if len(split) == 2:
            # Session, Player
            return split[0], split[1]
        else:
            self.send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid ping message received {message}")
