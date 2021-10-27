from abc import ABC, abstractmethod, ABCMeta
from typing import Tuple, Dict, List, TypeVar, Generic

from model.player import Player
from model.session import Session
from utils import logger
from utils.singleton import Singleton
from utils.uuid import UUIDGenerator

# TODO CHECK IF REMOVING A PLAYER UPDATES THE SESSIONS BY ADDRESS

S = TypeVar("S", bound=Session)
P = TypeVar("P", bound=Player)


class MetaSessionManager(ABCMeta, Singleton):
    pass


class SessionManager(ABC, Generic[S, P], metaclass=MetaSessionManager):

    def __init__(self):
        self._logger = logger.get_logger(self.__class__.__name__)
        self._uuid_generator: UUIDGenerator = UUIDGenerator()

    @abstractmethod
    def get_type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_sessions_by_name(self) -> Dict[str, S]:
        raise NotImplementedError

    @abstractmethod
    def _get_sessions_by_address(self) -> Dict[Tuple[str, int], S]:
        raise NotImplementedError

    @abstractmethod
    def _generate_session(self, name: str, max_players: int, host: P, password: str = None) -> S:
        raise NotImplementedError

    def create(self, player: P, max_players: int, password: str = None) -> S:
        if self._is_session_already_created_for(player.get_address()):
            raise AddressAlreadyHasSession
        session_name: str = self._uuid_generator.get_uuid()
        while self._has_session(session_name):
            self._logger.error(f"Generated session name {session_name} is already registered, a new one will be "
                               f"generated but this should never happen!")
            session_name = self._uuid_generator.get_uuid()
        session: S = self._generate_session(session_name, max_players, player, password)
        self._get_sessions_by_name()[session_name] = session
        self._get_sessions_by_address()[player.get_address()] = session
        return session

    def get(self, session_name: str) -> S:
        session: S = self._get_sessions_by_name().get(session_name)
        if not session:
            raise NonExistentSession
        return session

    def get_by_address(self, address: Tuple[str, int]) -> S:
        session: S = self._get_sessions_by_address().get(address)
        if not session:
            raise NonExistentSession
        return session

    def get_all_sessions(self) -> List[S]:
        return list(self._get_sessions_by_name().values())

    def delete(self, session_name: str):
        if self._has_session(session_name):
            session_to_delete: S = self._get_sessions_by_name()[session_name]
            for address, session in [key_value for key_value in self._get_sessions_by_address().items()]:
                if session_to_delete == session:
                    del self._get_sessions_by_address()[address]
                    break
            del self._get_sessions_by_name()[session_name]
        else:
            self._logger.debug(f"Session {session_name} is already deleted")
        self._uuid_generator.free_uuid(session_name)

    def _has_session(self, session_name: str) -> bool:
        return bool(self._get_sessions_by_name().get(session_name))

    def _is_session_already_created_for(self, address: Tuple[str, int]) -> bool:
        return bool(self._get_sessions_by_address().get(address))


class SessionManagerException(Exception):
    pass


class AddressAlreadyHasSession(SessionManagerException):
    pass


class NonExistentSession(SessionManagerException):
    pass
