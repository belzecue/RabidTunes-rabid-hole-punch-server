from abc import ABC, abstractmethod


class Handler(ABC):

    @abstractmethod
    def test(self):
        pass
