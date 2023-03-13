from os import getenv

from dotenv import load_dotenv

load_dotenv()


WELCOME_MESSAGES = getenv("WELCOME_MESSAGES", "").split(",")
