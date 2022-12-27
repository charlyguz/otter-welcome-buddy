from otter_welcome_buddy.formatters.debug import Formatter


def test_botIsReady():
    assert Formatter.bot_is_ready() == "Ready"
