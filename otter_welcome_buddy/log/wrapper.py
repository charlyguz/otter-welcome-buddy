import logging
from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import cast


def log_function(level: int = logging.INFO, message: str | None = None) -> Callable[..., Any]:
    """Decorator to log that the function is being called"""

    def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        logmsg = message if message else func.__module__ + "." + func.__name__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            # We need to create proper class to init Logger instead of setting log level
            logging.getLogger().setLevel(logging.INFO)
            logging.log(level, logmsg)
            return cast(Callable, func(*args, **kwargs))

        return wrapper

    return decorate
