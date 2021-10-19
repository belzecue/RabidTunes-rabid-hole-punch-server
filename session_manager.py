from typing import Dict

from utils.singleton import Singleton


class SessionManager(metaclass=Singleton):
    active_sessions = {}

    def get_sessions(self) -> Dict:
        return self.active_sessions
