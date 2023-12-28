from os import getenv

from dotenv import load_dotenv

load_dotenv()


BOT_TIMEZONE: str = "America/Mexico_City"

WELCOME_MESSAGES = getenv("WELCOME_MESSAGES", "").split(",")
