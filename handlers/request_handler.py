from abc import ABC, abstractmethod
from logging import Logger
from typing import Tuple

from twisted.internet.defer import inlineCallbacks

from session_manager import SessionManager
from utils import logger
from utils.thread import sleep

MAX_RETRIES: int = 20
SECONDS_TO_RETRY: float = 0.1


class RequestHandler(ABC):

    def __init__(self, transport):
        self._logger: Logger = logger.get_logger(self.__class__.__name__)
        self._session_manager: SessionManager = SessionManager()
        self._transport = transport  # Internal Twisted Transport Protocol, type not specified to avoid warnings

    @inlineCallbacks
    def send_message(self, address: Tuple[str, int], message: str, retries: int = 1):
        # TryExcept is required because @inlineCallbacks wraps this piece of code so
        # external TryExcept won't catch exceptions thrown here
        try:
            if retries <= 1:
                self._transport.write(bytes(message, "utf-8"), address)
                return

            for i in range(min(retries, MAX_RETRIES)):
                self._transport.write(bytes(message, "utf-8"), address)
                yield sleep(SECONDS_TO_RETRY)
        except Exception as e:
            self._logger.error("Uncontrolled error: %s", str(e))

    @abstractmethod
    def get_message_prefix(self) -> str:
        raise Exception

    @abstractmethod
    def handle_message(self, message: str, address: Tuple[str, int]):
        raise Exception
