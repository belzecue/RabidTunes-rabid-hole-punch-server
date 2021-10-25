from abc import ABC, abstractmethod
from typing import Dict

from twisted.internet import reactor

from utils import logger


class Scheduler(ABC):

    def __init__(self, args: Dict = None, auto_schedule: bool = True):
        if args is None:
            args = {}
        self._args: Dict = args
        self._scheduling: bool = True
        self._logger = logger.get_logger(self.__class__.__name__)
        if auto_schedule:
            self._schedule()

    @abstractmethod
    def get_seconds_for_next_execution(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def _schedule(self):
        reactor.callLater(self.get_seconds_for_next_execution(), self._run_and_reschedule)

    def _run_and_reschedule(self):
        self.run()
        if self._scheduling:
            reactor.callLater(self.get_seconds_for_next_execution(), self._run_and_reschedule)
