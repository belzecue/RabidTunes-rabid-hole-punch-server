from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import deferLater


class Potato:

    def __init__(self):
        pass

    @inlineCallbacks
    def potate(self):
        try:
            yield self.sleep(10)
            print("iM A POTATO")
        except Exception as e:
            print("EXCEPTIONNNN")

    def sleep(self, seconds):
        return deferLater(reactor, seconds, lambda: None)
