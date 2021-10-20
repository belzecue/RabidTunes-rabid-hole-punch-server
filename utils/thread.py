from twisted.internet import reactor
from twisted.internet.task import deferLater


def sleep(seconds):
    return deferLater(reactor, seconds, lambda: None)
