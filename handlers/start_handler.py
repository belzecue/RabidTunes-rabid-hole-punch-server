from typing import Tuple, List

from twisted.internet.defer import inlineCallbacks

from errors import ERR_SESSION_PLAYER_NON_HOST, ERR_SESSION_SINGLE_PLAYER, ERR_SESSION_NON_EXISTENT, \
    ERR_SESSION_PLAYER_NON_EXISTENT
from handlers.session_player_handler import SessionPlayerHandler
from model import Session, InvalidRequest, IgnoredRequest, NonExistentPlayer, Player
from session_manager import NonExistentSession
from utils.thread import sleep

START_REQUEST_PREFIX: str = "s"

_CONFIRMATION_RETRIES: int = 8
_SECONDS_BETWEEN_CONFIRMATION_RETRIES: float = 0.1


class StartHandler(SessionPlayerHandler):

    def get_message_prefix(self) -> str:
        return START_REQUEST_PREFIX

    def handle_message(self, message: str, address: Tuple[str, int]):
        session_name, player_name = self._parse_session_player_message_from(message, address)
        self._logger.debug(f"Received start request from player {player_name} in session {session_name}. "
                           f"Source: {address}")

        try:
            session: Session = self._session_manager.get(session_name)

            if not session.is_host(address):
                self._logger.debug(f"Requester address {address} is not host, cannot accept start request")
                self._send_message(address, ERR_SESSION_PLAYER_NON_HOST)
                raise InvalidRequest("Requester is not host, cannot accept start request")

            if session.has_started():
                self._logger.debug(f"Session {session_name} already started")
                raise IgnoredRequest

            if len(session.get_players()) == 1:
                self._logger.debug(f"Cannot start session {session_name} with only one player")
                self._send_message(address, ERR_SESSION_SINGLE_PLAYER)
                raise InvalidRequest(f"Cannot start session {session_name} with only one player")

            session.start()
            self._broadcast_starting_session(session)
        except NonExistentSession:
            self._logger.debug(f"Session {session_name} does not exist")
            self._send_message(address, ERR_SESSION_NON_EXISTENT)
        except NonExistentPlayer:
            self._logger.debug(f"Player to kick {player_name} does not exist in session {session_name}")
            self._send_message(address, ERR_SESSION_PLAYER_NON_EXISTENT)

    @inlineCallbacks
    def _broadcast_starting_session(self, session: Session):
        # TryExcept is required because @inlineCallbacks wraps this piece of code so
        # external TryExcept won't catch exceptions thrown here
        try:
            for i in range(_CONFIRMATION_RETRIES):
                # Create a copy of the list so we can avoid concurrency problems
                # because this function can (and will) be executed in parallel with other handlers
                # and we can run into concurrency issues within the loop when accessing the same list
                player_list_copy: List[Player] = list(session.get_players())

                if not player_list_copy:
                    # If no players are in list it means all players confirmed the address reception
                    # so no need to send more messages
                    break

                for player in player_list_copy:
                    self._send_message(player.get_address(),
                                      f"{START_REQUEST_PREFIX}"
                                      f":{player.port}"
                                      f":{session.get_players_addresses_except(player)}")
                yield sleep(_SECONDS_BETWEEN_CONFIRMATION_RETRIES)

            self._session_manager.delete(session.name)
            self._logger.info(f"All addresses sent for session {session.name}. Session closed.")
        except IgnoredRequest:
            pass
        except InvalidRequest as e:
            self._logger.debug(f"Invalid request: {str(e)}")
        except Exception as e:
            self._logger.error(f"Uncontrolled error: {str(e)}")
