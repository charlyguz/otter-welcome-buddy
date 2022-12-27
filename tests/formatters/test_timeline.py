import pytest

from otter_welcome_buddy.formatters.timeline import Formatter


def test_noValidMonthRaiseException():
    with pytest.raises(ValueError):
        Formatter.get_hiring_events_for(-1)
        Formatter.get_hiring_events_for(0)
        Formatter.get_hiring_events_for(13)


def test_summerInternshipHiringTimeline():
    summer_message = "Internship application opened for: Summer Internships 🏝️"
    assert Formatter.get_hiring_events_for(10) == summer_message
    assert Formatter.get_hiring_events_for(11) == summer_message
    assert Formatter.get_hiring_events_for(12) == summer_message
    assert Formatter.get_hiring_events_for(1) == summer_message


def test_fallInternshipHiringTimeline():
    fall_message = "Internship application opened for: Fall Internships 🍂"
    assert Formatter.get_hiring_events_for(4) == fall_message
    assert Formatter.get_hiring_events_for(5) == fall_message


def test_winterInternshipHiringTimeline():
    winter_message = "Internship application opened for: Wintern Internships ⛄"
    assert Formatter.get_hiring_events_for(8) == winter_message
    assert Formatter.get_hiring_events_for(9) == winter_message


def test_noSeasionHiringTimeline():
    no_season_message = (
        "Internship application opened for: Not this month, try next one 🦦"
    )
    assert Formatter.get_hiring_events_for(2) == no_season_message
    assert Formatter.get_hiring_events_for(3) == no_season_message
    assert Formatter.get_hiring_events_for(6) == no_season_message
    assert Formatter.get_hiring_events_for(7) == no_season_message
