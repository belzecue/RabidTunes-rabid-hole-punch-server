"""
Handlers package contains the handlers for the message this server
can receive. By extending the abstract class RequestHandler, server will
find and build it and use it in incoming requests
"""

# This is required in order for the server to find all the handlers without having to import
# the files one by one
from os import listdir
from os.path import dirname, basename

__all__ = [basename(f)[:-3] for f in listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]
