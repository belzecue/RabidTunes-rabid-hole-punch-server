from abc import ABC, abstractmethod

from utils import logger


class RequestHandler(ABC):

    def __init__(self):
        self.logger = logger.get_logger(self.__class__.__name__)

    @abstractmethod
    def get_message_prefix(self) -> str:
        raise Exception

    @abstractmethod
    def handle_message(self, message: str, address: tuple):
        pass
