from typing import Tuple

from errors import ERR_SESSION_NOT_STARTED, ERR_SESSION_NON_EXISTENT, ERR_SESSION_PLAYER_NON_EXISTENT
from handlers.session_player_handler import SessionPlayerHandler
from model import Session, InvalidRequest, NonExistentPlayer, Player
from session_manager import NonExistentSession

_CONFIRM_REQUEST_PREFIX: str = "y"


class ConfirmHandler(SessionPlayerHandler):

    def get_message_prefix(self) -> str:
        return _CONFIRM_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received confirmation about addresses reception for session {session_name} "
                           f"from player {player_name} Source: {address}")
        try:
            session: Session = self._session_manager.get(session_name)

            if not session.has_started():
                self._logger.debug(f"Session {session_name} is not started")
                self._send_message(address, ERR_SESSION_NOT_STARTED)
                raise InvalidRequest(f"Session {session_name} is not starting")

            player: Player = session.get_player(player_name)
            session.remove_player(player.name)
            self._logger.info(f"Player {player_name} from session {session_name} confirmed reception "
                              f"of other players' addresses")

        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player to confirm {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)
