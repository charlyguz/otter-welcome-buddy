from datetime import datetime

from apscheduler.triggers.cron import CronTrigger

from otter_welcome_buddy.settings import BOT_TIMEZONE


class DateUtils:
    """Utility class for datetime python library"""

    @staticmethod
    def get_current_month() -> int:
        """Get current number month"""
        return datetime.now().month

    @staticmethod
    def create_cron_trigger_from(crontab: str) -> CronTrigger:
        """Returns cron trigger from crontab"""
        return CronTrigger.from_crontab(crontab, BOT_TIMEZONE)
