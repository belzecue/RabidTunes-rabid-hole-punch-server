# InvalidRequest represents some kind of error when processing the incoming request
class InvalidRequest(Exception):
    pass


# IgnoredRequest represents that the request was ignored because it does not apply to current session/player state
class IgnoredRequest(Exception):
    pass
