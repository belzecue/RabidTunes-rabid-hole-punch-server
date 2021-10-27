"""
Server is the class that routes the requests
to the appropriate handler

There are a couple #noinspection statements, this is needed so those imports
won't be marked as unused and deleted by accident. They are required so
server can detect new handlers and schedulers without the need to manually add
the import here
"""
from inspect import isabstract
from typing import Tuple

from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import DatagramProtocol

from constants.exceptions import IgnoredRequest, InvalidRequest
from service.schedulers.abc_message_sender_scheduler import SEND_MESSAGE_NAME
from service.schedulers.abc_scheduler import Scheduler
from utils import logger
from constants.errors import *

from service.handlers.abc_request_handler import RequestHandler
# noinspection PyUnresolvedReferences
from service.handlers import *
# noinspection PyUnresolvedReferences
from service.schedulers import *
from utils.reflection import get_all_subclasses
from utils.thread import sleep

_SEND_MESSAGE_MAX_RETRIES: int = 20
_SECONDS_TO_NEXT_MESSAGE_RETRY: float = 0.1


class Server(DatagramProtocol):

    def __init__(self):
        self._logger = logger.get_logger("Server")
        self._handlers = {}
        self._schedulers = {}
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
            self._logger.debug(f"{handler.__class__.__name__} loaded and listening for '{handler.get_message_prefix()}'"
                               f" requests")

    def _initialize_schedulers(self):
        all_schedulers: set = get_all_subclasses(Scheduler)
        for scheduler_class in all_schedulers:
            if isabstract(scheduler_class):
                continue
            scheduler = scheduler_class({SEND_MESSAGE_NAME: self._send_message}, True)
            self._schedulers[scheduler.__class__.__name__] = scheduler
            self._logger.debug(f"{scheduler.__class__.__name__} loaded, will execute each "
                               f"{scheduler.get_seconds_for_next_execution()} seconds")

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

            for i in range(min(retries, _SEND_MESSAGE_MAX_RETRIES)):
                self.transport.write(bytes(message, "utf-8"), address)
                yield sleep(_SECONDS_TO_NEXT_MESSAGE_RETRY)
        except Exception as e:
            self._logger.error(f"Uncontrolled error: {str(e)}")
