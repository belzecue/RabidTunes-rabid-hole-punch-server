from abc import ABC

from handlers.request_handler import RequestHandler, INFO_PREFIX
from model import Session


class SessionBroadcasterHandler(RequestHandler, ABC):

    def _broadcast_session_info(self, session: Session):
        for player in session.get_players():
            self._send_message((player.ip, player.port), ":".join([INFO_PREFIX] + session.get_player_names()))
