import logging
from functools import wraps


def log_function(level=logging.INFO, message=None):
    """Decorator to log that the function is being called"""

    def decorate(func):
        logmsg = message if message else func.__module__ + "." + func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            # We need to create proper class to init Logger instead of setting log level
            logging.getLogger().setLevel(logging.INFO)
            logging.log(level, logmsg)
            return func(*args, **kwargs)

        return wrapper

    return decorate
