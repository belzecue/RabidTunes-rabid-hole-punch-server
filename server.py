"""
Server is the class that routes the requests
to the appropiate handler
TODO ADD EXPLANATION ON IMPORT AND NOINSPECTION
"""
from inspect import isabstract
from typing import Tuple

from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol

from service.schedulers.message_sender_scheduler import SEND_MESSAGE_NAME
from service.schedulers.scheduler import Scheduler
from service.session_managers.session_manager import SessionManager
from utils import logger
from constants.errors import *

from service.handlers.request_handler import RequestHandler
# noinspection PyUnresolvedReferences
from service.handlers import *
# noinspection PyUnresolvedReferences
from service.schedulers import *
from utils.reflection import get_all_subclasses
from utils.thread import sleep

_MAX_RETRIES: int = 20
_SECONDS_TO_RETRY: float = 0.1


class Server(DatagramProtocol):

    def __init__(self):
        self._logger = logger.get_logger("Server")
        self._handlers = {}
        self._schedulers = {}
        self._session_manager = SessionManager()
        self._initialize_request_handlers()
        self._initialize_schedulers()

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

    def _initialize_schedulers(self):
        all_schedulers: set = get_all_subclasses(Scheduler)
        for scheduler_class in all_schedulers:
            if isabstract(scheduler_class):
                continue
            scheduler = scheduler_class({SEND_MESSAGE_NAME: self._send_message}, True)
            self._schedulers[scheduler.__class__.__name__] = scheduler
            self._logger.debug(f"{scheduler.__class__.__name__} loaded")

    def datagramReceived(self, datagram, address):
        datagram_string = datagram.decode("utf-8")
        self._logger.debug(f"Received datagram {datagram_string}")

        try:
            message_type, message = self._parse_datagram_string(datagram_string, address)
            if message_type not in self._handlers.keys():
                raise InvalidRequest("Unknown message type")
            self._handlers[message_type].handle_message(message, address)
        except IgnoredRequest:
            pass
        except InvalidRequest as e:
            self._logger.debug(f"Invalid request: {str(e)}")
        except Exception as e:
            self._logger.error(f"Uncontrolled error: {str(e)}")

    def _parse_datagram_string(self, data_string: str, address: Tuple[str, int]) -> Tuple[str, str]:
        split = data_string.split(":", 1)
        if len(split) != 2:
            self._logger.debug(f"Invalid datagram received {data_string}")
            self._send_message(address, ERR_INVALID_REQUEST)
            raise InvalidRequest(f"Invalid datagram received {data_string}")
        # MessageType, Message
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


class InvalidRequest(Exception):
    pass


class IgnoredRequest(Exception):
    pass
