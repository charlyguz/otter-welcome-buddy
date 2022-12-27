from otter_welcome_buddy.formatters.messages import Formatter


def test_welcome_message():
    assert Formatter.welcome_message() == "Welcome to Proyecto Nutria"
