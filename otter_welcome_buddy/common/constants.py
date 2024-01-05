import os
from enum import Enum


class CronExpressions(Enum):
    """Defined Cron Expressions"""

    DAY_ONE_OF_EACH_MONTH_CRON: str = "0 0 1 * *"


COMMAND_PREFIX: str = "!"

FONT_PATH: str = "assets/fonts/Inter-Regular.ttf"

DATA_DIR: str = "data"
DATA_FILE: str = "otter-buddy.db"
DATA_FILE_PATH: str = os.path.join(DATA_DIR, DATA_FILE)

LOG_DIR: str = "logs"
LOG_FILE: str = "otter-buddy.log"
LOG_FILE_PATH: str = os.path.join(LOG_DIR, LOG_FILE)

ALL_DIRS = (
    attrib_value
    for attrib_name, attrib_value in list(globals().items())
    if attrib_name.endswith("DIR")
)

# Discord role that give access to admin role based commands
OTTER_ADMIN: str = "ROOT"
# Discord role that give access to moderator role based commands
OTTER_MODERATOR: str = "Collaborator"
# Discord role that give access to the remaining channels and is
# given when the user react to WELCOME_MESSAGES
OTTER_ROLE: str = "Interviewee"

WELCOME_MESSAGES: dict[int, list[int]] = {}
