"""
Server is the class that routes the requests
to the appropiate handler
"""
from inspect import isabstract
from typing import Tuple, List

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol

from session_manager import SessionManager
from utils import logger
from errors import *

from handlers.request_handler import RequestHandler
from model import Session, InvalidRequest, IgnoredRequest
# This "from handlers import *" is used to dynamically load the request handlers
# Do not remove the 'noinspection' statement otherwise you might delete it when optimizing imports
# noinspection PyUnresolvedReferences
from handlers import *
from utils.reflection import get_all_subclasses
from utils.thread import sleep

_SCHEDULED_SESSION_CLEANUP_SECONDS: float = 60 * 5
_SCHEDULED_PLAYER_CLEANUP_SECONDS: float = 8


_MAX_RETRIES: int = 20
_SECONDS_TO_RETRY: float = 0.1


class Server(DatagramProtocol):

    def __init__(self):
        self._logger = logger.get_logger("Server")
        self._handlers = {}
        self._session_manager = SessionManager()
        self._initialize_request_handlers()
        reactor.callLater(_SCHEDULED_SESSION_CLEANUP_SECONDS, self._cleanup_sessions)
        reactor.callLater(_SCHEDULED_PLAYER_CLEANUP_SECONDS, self._cleanup_players)

    def datagramReceived(self, datagram, address):
        datagram_string = datagram.decode("utf-8")
        self._logger.debug(f"Received datagram {datagram_string}")

        try:
            message_type, message = self._parse_datagram_string(datagram_string, address)
            if message_type not in self._handlers.keys():
                raise InvalidRequest
            self._handlers[message_type].handle_message(message, address)
        except IgnoredRequest:
            pass
        except InvalidRequest as e:
            self._logger.debug(f"Invalid request: {str(e)}")
        except Exception as e:
            self._logger.error(f"Uncontrolled error: {str(e)}")

    def _parse_datagram_string(self, data_string: str, address: Tuple) -> Tuple:
        split = data_string.split(":", 1)
        if len(split) != 2:
            self._logger.debug(f"Invalid datagram received {data_string}")
            self._send_message(address, ERR_REQUEST_INVALID)
            raise InvalidRequest(f"Invalid datagram received {data_string}")
        return split[0], split[1]

    @inlineCallbacks
    def _send_message(self, address: Tuple[str, int], message: str, retries: int = 1):
        # TryExcept is required because @inlineCallbacks wraps this piece of code so
        # external TryExcept won't catch exceptions thrown here
        try:
            if retries <= 1:
                self.transport.write(bytes(message, "utf-8"), address)
                return

            for i in range(min(retries, _MAX_RETRIES)):
                self.transport.write(bytes(message, "utf-8"), address)
                yield sleep(_SECONDS_TO_RETRY)
        except Exception as e:
            self._logger.error(f"Uncontrolled error: {str(e)}")

    def _initialize_request_handlers(self):
        all_handlers: set = get_all_subclasses(RequestHandler)
        for handler_class in all_handlers:
            if isabstract(handler_class):
                continue
            handler = handler_class(self._send_message)
            if handler.get_message_prefix() in self._handlers.keys():
                raise Exception(f"Duplicated handler for {handler.get_message_prefix()}")
            self._handlers[handler.get_message_prefix()] = handler
            self._logger.debug(f"{handler.__class__.__name__} loaded")

    """
    Async background tasks
    """
    def _cleanup_sessions(self):
        all_sessions: List[Session] = list(self._session_manager.get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting session cleanup")

        for session in all_sessions:
            if session.is_timed_out():
                self._session_manager.delete(session.name)
                for player in session.get_players():
                    self._send_message(player.get_address(), ERR_SESSION_TIMEOUT, 3)
                self._logger.info(f"Session {session.name} deleted because it timed out")
        reactor.callLater(_SCHEDULED_SESSION_CLEANUP_SECONDS, self._cleanup_sessions)

    def _cleanup_players(self):
        all_sessions: List[Session] = list(self._session_manager.get_all_sessions())
        if all_sessions:
            self._logger.debug("Starting player cleanup")

        for session in all_sessions:
            to_kick = [player for player in session.get_players() if player.is_timed_out()]
            for player in to_kick:
                session.remove_player(player.name)
                self._send_message(player.get_address(), ERR_PLAYER_TIMEOUT, 3)
                self._logger.info(f"Kicked player {player.name} from session {session.name} because it timed out")
            if not session.has_players():
                self._session_manager.delete(session.name)
                self._logger.info(f"No more players in session {session.name}, deleted session")
                continue
        reactor.callLater(_SCHEDULED_PLAYER_CLEANUP_SECONDS, self._cleanup_players)

    """
    def realtime_host_session(self, message: str, address: Tuple):
        player_name, max_players, password = self.parse_realtime_host_request(message, address)
        ip, port = address
        self._logger.debug("Received request from player %s to host a realtime session for max %s players. "
                          "Source: %s:%s", player_name, max_players, ip, port)
        session: Session = self.sessions_by_address.get(address)
        if session:
            if session.password_matches(password):
                self.send_message(address, f"ok:{session.name}:{session.secret}")
                return
            else:
                self._logger.debug("Session password for session %s does not match", session.name)
                self.send_message(address, ERR_SESSION_PASSWORD_MISMATCH)
                raise InvalidRequest(f"Session password for session {session.name} does not match")

        session_code: str = get_random_string_from(SESSION_NAME_CHARACTERS, SESSION_NAME_LENGTH)
        session_secret: str = get_random_string_from(UUID_CHARACTERS, SECRET_LENGTH)
        session = Session(session_code, max_players, Player(player_name, ip, port), password, session_secret)

        self.active_sessions[session.name] = session
        self.sessions_by_address[address] = session
        self._logger.info("Created session %s (max %s players)", session.name, max_players)
        self.send_message(address, f"ok:{session.name}:{session.secret}")

    def realtime_ping(self, message: str, address: Tuple):
        session_name: str = message
        ip, port = address
        # TODO Update last seen for this session
        # TODO Send all players: Confirmed players only name, non-confirmed players send name/ip/port

    def realtime_connect_session(self, message: str, address: Tuple):
        session_name, player_name, session_password = self.parse_connect_request(message, address)
        ip, port = address
        self._logger.debug("Received request from player %s to connect to realtime session %s. Source: %s:%s",
                           player_name, session_name, ip, port)
        # TODO Check if player list is full
        # TODO Check if player is in list, if is in list but no host port assigned, send wait, send host port otherwise
        # TODO Add player to list of candidates
        # TODO Send message to host informing about new player
        # TODO Send message to client saying wait

    def realtime_host_port_info(self, message: str, address: Tuple):
        session_name, session_secret = self.parse_host_port_request(message, address)
        ip, port = address
        self._logger.debug("Received request from to add host port info for new player")
        # TODO Pair new host port to latest player candidate
        # TODO Send ok to host so the host can start paying attention to new player and sending greetings

    def realtime_player_confirmed_by_host(self, message: str, address: Tuple):
        pass
        # TODO Move player from candidate list to confirmed player list, start sending this player in the pings
        # TODO Leave place for a new candidate if there's room for it
    """

