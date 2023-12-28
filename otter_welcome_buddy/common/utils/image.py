import os

from discord import Member
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL.Image import Image as ImageType
from PIL.ImageDraw import ImageDraw as ImageDrawType
from PIL.ImageFont import FreeTypeFont

from otter_welcome_buddy.common.constants import FONT_PATH

_DEFAULT_IMAGE_PATH: str = os.path.dirname(os.path.realpath(__file__)) + "/image.jpg"
_COLOR_TEXT: str = "black"
_COLOR_OUTLINE: str = "gray"
_COLOR_BACKGROUND: str = "white"
_FONT_SIZE: int = 16
_MARGIN_RIGHT: int = 30
_MARGIN_TOP: int = 10


def _get_size(txt: str, font: FreeTypeFont) -> tuple[int, int]:
    """
    Get the size (height, width) of the text provided based on the font in píxels
    """
    temp_img: ImageType = Image.new("RGB", (1, 1))
    temp_draw: ImageDrawType = ImageDraw.Draw(temp_img)
    _, _, text_width, text_height = temp_draw.textbbox((0, 0), txt, font)
    return text_width, text_height


def create_match_image(
    week_otter_pairs: list[tuple[Member, Member]],
) -> tuple[ImageType, str]:
    """
    Create a jpg image with the pairs of participants
    """
    first_list, second_list = zip(*week_otter_pairs)
    first_column: str = "\n".join(
        list(map(lambda user: f"{user.display_name}", first_list)),
    )
    second_column: str = "\n".join(
        list(
            map(lambda user: f"{user.display_name}", second_list),
        ),
    )

    # TODO: except image creation errors
    font: FreeTypeFont = ImageFont.truetype(FONT_PATH, _FONT_SIZE)

    width, height = _get_size(first_column, font)
    width2, height2 = _get_size(second_column, font)
    max_height: int = max(height, height2)
    img: ImageType = Image.new(
        "RGB",
        ((width + width2) + (_MARGIN_RIGHT * 2), (max_height) + (_MARGIN_TOP * 2)),
        _COLOR_BACKGROUND,
    )
    image_canvas: ImageDrawType = ImageDraw.Draw(img)
    image_canvas.text(
        (_MARGIN_RIGHT / 2, _MARGIN_TOP / 2),
        first_column,
        fill=_COLOR_TEXT,
        font=font,
    )
    image_canvas.text(
        (width + _MARGIN_RIGHT + (_MARGIN_RIGHT / 2), _MARGIN_TOP / 2),
        second_column,
        fill=_COLOR_TEXT,
        font=font,
    )
    image_canvas.rectangle(
        (0, 0, width + _MARGIN_RIGHT, max_height + (_MARGIN_TOP * 2)),
        outline=_COLOR_OUTLINE,
    )
    image_canvas.rectangle(
        (
            width + _MARGIN_RIGHT,
            0,
            (width + width2) + (_MARGIN_RIGHT * 2),
            max_height + (_MARGIN_TOP * 2),
        ),
        outline=_COLOR_OUTLINE,
    )

    img.save(_DEFAULT_IMAGE_PATH)

    return img, _DEFAULT_IMAGE_PATH
