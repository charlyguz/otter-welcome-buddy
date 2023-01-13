from datetime import datetime

from apscheduler.triggers.cron import CronTrigger  # type: ignore


class DateUtils:
    """Utility class for datetime python library"""

    @staticmethod
    def get_current_month() -> int:
        """Get current number month"""
        return datetime.now().month

    @staticmethod
    def create_cron_trigger_from(crontab: str) -> CronTrigger:
        """Returns cron trigger from crontab"""
        return CronTrigger.from_crontab(crontab)
