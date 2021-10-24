"""
Helper file to store all regular expressions in one place so it is easier to keep track and
add new regular expressions or modify the existent ones
"""

PLAYER_NAME_REGEX: str = "^[A-Za-z0-9]{1,12}$"
MAX_PLAYERS_REGEX: str = "^([2-9]|1[0-2])$"
SESSION_PASS_REGEX: str = "^[A-Za-z0-9]{1,12}$"
SESSION_NAME_REGEX: str = "^[A-Z0-9]{1,10}$"
