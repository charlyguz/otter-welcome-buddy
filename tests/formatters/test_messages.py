from otter_welcome_buddy.formatters.messages import Formatter


def test_welcomeMessage():
    assert Formatter.welcome_message() == "Welcome to Proyecto Nutria"
