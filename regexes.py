"""
Helper file to store all regular expressions in one place so it is easier to keep track and
add new regular expressions or modify the existent ones
"""

PLAYER_NAME_REGEX = "^[A-Za-z0-9]{1,12}$"
MAX_PLAYERS_REGEX = "^([2-9]|1[0-2])$"
SESSION_PASS_REGEX = "^[A-Za-z0-9]{1,12}$"
SESSION_NAME_REGEX = "^[A-Z0-9]{1,10}$"
