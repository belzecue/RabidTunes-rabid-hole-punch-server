from abc import ABC
from typing import Callable, Dict

from service.schedulers.scheduler import Scheduler

SEND_MESSAGE_NAME: str = "send_message_function"


class MessageSenderScheduler(Scheduler, ABC):

    def __init__(self, args: Dict = None, auto_schedule: bool = True):
        super().__init__(args, auto_schedule)
        self._send_message: Callable = args[SEND_MESSAGE_NAME]
