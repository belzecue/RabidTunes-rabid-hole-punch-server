"""
Schedulers package contains the schedulers that will run in the background
By extending the abstract class Scheduler, server will find, build and start them
"""

# This is required in order for the server to find all the schedulers without having to import
# the files one by one
from os import listdir
from os.path import dirname, basename

__all__ = [basename(f)[:-3] for f in listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]
