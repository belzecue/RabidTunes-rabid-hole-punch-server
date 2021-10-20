from typing import Tuple, Dict

from model import Session, Player
from utils import logger
from utils.singleton import Singleton
from utils.uuid import UUIDGenerator


class SessionManager(metaclass=Singleton):

    def __init__(self):
        self._logger = logger.get_logger(self.__class__.__name__)
        self._sessions_by_address: Dict[Tuple[str, int], Session] = {}
        self._active_sessions: Dict[str, Session] = {}
        self._uuid_generator: UUIDGenerator = UUIDGenerator()

    def create(self, player: Player, max_players: int, password: str = None) -> Session:
        if self.is_session_already_created_for(player.get_address()):
            raise AddressAlreadyHasSession
        session_name: str = self._uuid_generator.get_uuid()
        while self.exists(session_name):
            self._logger.error("Generated session name %s is already registered, a new one will be generated but this "
                               "should never happen!", session_name)
            session_name = self._uuid_generator.get_uuid()
        session: Session = Session(session_name, max_players, player, password)
        self._active_sessions[session_name] = session
        self._sessions_by_address[player.get_address()] = session
        return session

    def get(self, session_name: str) -> Session:
        session: Session = self._active_sessions.get(session_name)
        if not session:
            raise NonExistentSession
        return session

    def get_by_address(self, address: Tuple[str, int]) -> Session:
        session: Session = self._sessions_by_address.get(address)
        if not session:
            raise NonExistentSession
        return session

    def has_session(self, session_name: str) -> bool:
        return bool(self._active_sessions[session_name])

    def add(self, session: Session):
        if self.exists(session.name) or self.is_session_already_created_for(session.host.get_address()):
            raise Exception  # TODO
        self._active_sessions[session.name] = session
        self._sessions_by_address[session.host.get_address()] = session

    def exists(self, session_name: str) -> bool:
        return bool(self._active_sessions.get(session_name))

    def is_host_for(self, address: Tuple[str, int], session_name: str) -> bool:
        session_obj: Session = self._active_sessions.get(session_name)
        if not session_obj:
            raise Exception  # TODO
        return (session_obj.host.ip, session_obj.host.port) == address

    def is_session_already_created_for(self, address: Tuple[str, int]) -> bool:
        return bool(self._sessions_by_address.get(address))

    def delete(self, session_name: str):
        if self.has_session(session_name):
            session_to_delete: Session = self._active_sessions[session_name]
            for address, session in self._sessions_by_address.items():
                if session_to_delete == session:
                    del self._sessions_by_address[address]
            del self._active_sessions[session_name]
        else:
            self._logger.debug("Session %s is already deleted")
        self._uuid_generator.free_uuid(session_name)


class SessionManagerException(Exception):
    pass


class AddressAlreadyHasSession(SessionManagerException):
    pass


class NonExistentSession(SessionManagerException):
    pass
