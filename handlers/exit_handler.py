from typing import Tuple

from errors import ERR_PLAYER_ADDRESS_EXIT_MISMATCH, ERR_SESSION_PLAYER_EXIT, ERR_SESSION_NON_EXISTENT, \
    ERR_SESSION_PLAYER_NON_EXISTENT
from handlers.session_broadcaster_handler import SessionBroadcasterHandler
from handlers.session_player_handler import SessionPlayerHandler
from model import Session, Player, InvalidRequest, NonExistentPlayer
from session_manager import NonExistentSession

_EXIT_REQUEST_PREFIX: str = "x"


class ExitHandler(SessionPlayerHandler, SessionBroadcasterHandler):

    def get_message_prefix(self) -> str:
        return _EXIT_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received exit request from player {player_name} from session {session_name}. "
                           f"Source: {address}")

        try:
            session: Session = self._session_manager.get(session_name)
            if session.has_started():
                self._logger.debug(f"Session {session_name} already started cannot exit now")
                raise InvalidRequest("Session already started cannot accept exit request")

            player: Player = session.get_player(player_name)

            if not address == player.get_address():
                self._logger.debug(f"Requester address {address} is not same as player {player.name} stored address, "
                                   f"cannot accept exit request")
                self._send_message(address, ERR_PLAYER_ADDRESS_EXIT_MISMATCH)
                raise InvalidRequest("Requester is not same as exit player, cannot accept exit request")

            session.remove_player(player.name)
            self._send_message(address, ERR_SESSION_PLAYER_EXIT)

            if session.has_players():
                self._broadcast_session_info(session)
            else:
                self._session_manager.delete(session_name)
                self._logger.info(f"No more players in session {session_name}, deleted session")
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player to kick {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
