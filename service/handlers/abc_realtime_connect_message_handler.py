from abc import ABC

from service.handlers.abc_connect_message_handler import ConnectMessageHandler

_REALTIME_CONNECT_REQUEST_PREFIX: str = "rc"


class RealtimeConnectMessageHandler(ConnectMessageHandler, ABC):
    pass
