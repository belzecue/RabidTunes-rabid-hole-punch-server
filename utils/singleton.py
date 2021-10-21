"""
Helper class to implement singletons
"""
from threading import Lock
from typing import Dict

lock: Lock = Lock()
class_locks: Dict[str, Lock] = {}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Singleton init happens in 2 steps
        First get the lock for the given class, then try to create the singleton object using that class lock

        This is done because some singletons are initialized based on other singletons, and
        having just one lock for everything makes the system freeze
        (first singleton __init__() calls another singleton __init__() and they get stuck forever in the lock)

        Please note that this does not fix circular dependencies (example singleton A has references to singleton B
        in the __init__() method and singleton B has references to singleton A in __init__() method too)
        """
        class_lock: Lock
        with lock:
            class_lock = class_locks.get(cls.__name__)
            if not class_lock:
                class_lock = Lock()
                class_locks[cls.__name__] = class_lock

        if cls not in cls._instances:
            with class_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]






