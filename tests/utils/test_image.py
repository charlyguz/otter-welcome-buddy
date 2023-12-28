from collections.abc import Callable

import pytest
from discord import Member
from PIL import ImageFont
from PIL.Image import Image
from PIL.ImageFont import FreeTypeFont
from pytest_mock import MockFixture

from otter_welcome_buddy.common.constants import FONT_PATH
from otter_welcome_buddy.common.utils import image


@pytest.mark.parametrize(
    "font_size, expected_width, expected_height",
    [
        (10, 44, 11),
        (12, 52, 13),
        (15, 65, 16),
        (20, 87, 21),
    ],
)
def test__get_size(font_size: int, expected_width: int, expected_height: int) -> None:
    # Arrange
    font: FreeTypeFont = ImageFont.truetype(FONT_PATH, font_size)
    test_text: str = "Test Text"

    # Act
    result_width, result_height = image._get_size(test_text, font)

    # Assert
    assert result_width == expected_width
    assert result_height == expected_height


def test_create_match_image(
    mocker: MockFixture,
    make_mock_member: Callable[[int, str], Member],
) -> None:
    # Arrange
    mocked_member_list: list[tuple[Member, Member]] = [
        (make_mock_member(1, "Test1"), make_mock_member(2, "Test2")),
        (make_mock_member(3, "Test3"), make_mock_member(4, "Test4")),
    ]

    mock_save_image = mocker.patch.object(Image, "save")

    # Act
    result_image, result_path = image.create_match_image(mocked_member_list)

    # Assert
    mock_save_image.assert_called_once()
    assert result_image is not None
    assert "otter_welcome_buddy/common/utils/image.jpg" in result_path
