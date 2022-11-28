""" Formatters only for development """


class Formatter:
    """Dependency for debug messages"""

    @staticmethod
    def bot_is_ready():
        """It indicates when the bot is up and running"""
        return "Ready"

    @staticmethod
    def bot_is_ready_2():
        """Place holder to avoid problems with pylint"""
        return "Ready"
