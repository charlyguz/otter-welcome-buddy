from otter_welcome_buddy.startup import intents


def test_getRegisteredIntents_messageNMembers() -> None:
    # Arrange / Act
    registered_intents = intents.get_registered_intents()

    # Assert
    assert registered_intents.messages is True
    assert registered_intents.members is True
    assert registered_intents.reactions is True
