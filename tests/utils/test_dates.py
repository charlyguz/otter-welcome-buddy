from datetime import datetime
from datetime import timedelta

from otter_welcome_buddy.common.constants import CronExpressions
from otter_welcome_buddy.common.utils.dates import DateUtils


def test_datetime_returns_integer_month() -> None:
    # Act
    current_month = DateUtils.get_current_month()

    # Assert
    assert current_month == datetime.now().month
    assert isinstance(current_month, int)


def test_cron_creation_from_crontab() -> None:
    # Arrange
    dec_fixed_date = datetime(2022, 12, 30)

    # Act
    system_under_test = DateUtils.create_cron_trigger_from(
        CronExpressions.DAY_ONE_OF_EACH_MONTH_CRON.value,
    )
    jan_exec = system_under_test.get_next_fire_time(None, dec_fixed_date)
    feb_exec = system_under_test.get_next_fire_time(None, jan_exec + timedelta(days=1))
    mar_exec = system_under_test.get_next_fire_time(None, feb_exec + timedelta(days=1))
    apr_exec = system_under_test.get_next_fire_time(None, mar_exec + timedelta(days=1))
    may_exec = system_under_test.get_next_fire_time(None, apr_exec + timedelta(days=1))
    jun_exec = system_under_test.get_next_fire_time(None, may_exec + timedelta(days=1))
    jul_exec = system_under_test.get_next_fire_time(None, jun_exec + timedelta(days=1))
    aug_exec = system_under_test.get_next_fire_time(None, jul_exec + timedelta(days=1))
    sep_exec = system_under_test.get_next_fire_time(None, aug_exec + timedelta(days=1))
    oct_exec = system_under_test.get_next_fire_time(None, sep_exec + timedelta(days=1))
    nov_exec = system_under_test.get_next_fire_time(None, oct_exec + timedelta(days=1))
    dec_exec = system_under_test.get_next_fire_time(None, nov_exec + timedelta(days=1))

    # Assert
    assert datetime(2023, 1, 1).date() == jan_exec.date()
    assert datetime(2023, 2, 1).date() == feb_exec.date()
    assert datetime(2023, 3, 1).date() == mar_exec.date()
    assert datetime(2023, 4, 1).date() == apr_exec.date()
    assert datetime(2023, 5, 1).date() == may_exec.date()
    assert datetime(2023, 6, 1).date() == jun_exec.date()
    assert datetime(2023, 7, 1).date() == jul_exec.date()
    assert datetime(2023, 8, 1).date() == aug_exec.date()
    assert datetime(2023, 9, 1).date() == sep_exec.date()
    assert datetime(2023, 10, 1).date() == oct_exec.date()
    assert datetime(2023, 11, 1).date() == nov_exec.date()
    assert datetime(2023, 12, 1).date() == dec_exec.date()
