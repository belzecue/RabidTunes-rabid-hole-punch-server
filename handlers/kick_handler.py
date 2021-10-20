from typing import Tuple

from errors import ERR_REQUEST_INVALID, ERR_SESSION_PLAYER_NON_EXISTENT, ERR_SESSION_NON_EXISTENT, \
    ERR_SESSION_PLAYER_NON_HOST, ERR_SESSION_PLAYER_KICKED_BY_HOST
from handlers.request_handler import RequestHandler
from model import InvalidRequest, NonExistentPlayer, Session, Player
from session_manager import NonExistentSession

_KICK_REQUEST_PREFIX: str = "k"
_INFO_PREFIX: str = "i"


class KickHandler(RequestHandler):

    def get_message_prefix(self) -> str:
        return _KICK_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_ping_message_from(message, address)
        ip, port = address
        self._logger.debug("Received ping from player %s from session %s. Source: %s:%s",
                           player_name, session_name, ip, port)

        try:
            session: Session = self._session_manager.get(session_name)

            if not session.is_host(address):
                self._logger.debug("Requester address %s is not host, cannot accept kick request", address)
                self.send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Requester is not host, cannot accept kick request")

            if session.has_started():
                self._logger.debug("Session %s already started cannot kick now", session.name)
                raise InvalidRequest("Session already started cannot accept kick request")

            player_to_kick: Player = session.get_player(player_name)
            session.remove_player(player_to_kick.name)
            self.send_message(player_to_kick.get_address(), ERR_SESSION_PLAYER_KICKED_BY_HOST)

            if session.has_players():
                self._broadcast_session_info(session)
            else:
                self._session_manager.delete(session_name)
                self._logger.info("No more players in session %s, deleted session", session_name)
        except NonExistentSession:
            self._logger.debug("Session %s does not exist", session_name)
            self.send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug("Player to kick %s does not exist in session %s", player_name, session_name)
            self.send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)

    def _parse_ping_message_from(self, message: str, address: Tuple[str, int]) -> Tuple[str, str]:
        split = message.split(":")
        if len(split) == 2:
            # Session, Player
            return split[0], split[1]
        else:
            self.send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid ping message received {message}")

    def _broadcast_session_info(self, session: Session):
        for player in session.players_array:
            self.send_message((player.ip, player.port), ":".join([_INFO_PREFIX] + session.get_player_names()))
