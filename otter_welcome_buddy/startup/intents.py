"""An intent allows a bot to subscribe to specific buckets of events"""
from discord import Intents


def get_registered_intents() -> Intents:
    """Returns registered intents"""
    # Not registered intents cannot be used by bot
    intents: Intents = Intents.default()
    intents.message_content = True  # Send DMs
    intents.members = True  # Detect new members
    return intents
