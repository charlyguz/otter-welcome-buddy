import logging

from pymongo import monitoring


logger = logging.getLogger(__name__)


class DbCommandLogger(monitoring.CommandListener):
    """
    Custom MongoDB command logger that logs information about the execution of commands.

    Attributes:
        None

    Methods:
        started(event): Logs when a MongoDB command is started.
        succeeded(event): Logs when a MongoDB command succeeds.
        failed(event): Logs when a MongoDB command fails.
    """

    def started(self, event: monitoring.CommandStartedEvent) -> None:
        """
        This method is called when a MongoDB command is started.

        Args:
            event: The object containing information about the started command.
        """
        logger.info(
            "Command %s with request id %s started on server %s",
            event.command_name,
            event.request_id,
            event.connection_id,
        )

    def succeeded(self, event: monitoring.CommandStartedEvent) -> None:
        """
        This method is called when a MongoDB command succeeds.

        Args:
            event: The object containing information about the successful command.
        """
        logger.info(
            "Command %s with request id %s on server %s succeeded in %s microseconds",
            event.command_name,
            event.request_id,
            event.connection_id,
            event.duration_micros,
        )

    def failed(self, event: monitoring.CommandStartedEvent) -> None:
        """
        This method is called when a MongoDB command fails.

        Args:
            event: The object containing information about the failed command.
        """
        logger.info(
            "Command %s with request id %s on server %s failed in %s microseconds",
            event.command_name,
            event.request_id,
            event.connection_id,
            event.duration_micros,
        )
