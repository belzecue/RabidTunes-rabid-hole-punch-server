from abc import ABC, abstractmethod
from logging import Logger
from typing import Tuple, Callable

from service.session_managers.abc_session_manager import SessionManager
from utils import logger

INFO_PREFIX: str = "i"


class RequestHandler(ABC):

    def __init__(self, send_message_function: Callable):
        self._logger: Logger = logger.get_logger(self.__class__.__name__)
        self._send_message = send_message_function

    @abstractmethod
    def get_message_prefix(self) -> str:
        raise Exception

    @abstractmethod
    def handle_message(self, message: str, address: Tuple[str, int]):
        raise Exception
