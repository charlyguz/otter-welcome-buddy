import os

from common.constants import FONT_PATH
from discord import Member
from discord import User
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL.Image import Image as ImageType
from PIL.ImageDraw import ImageDraw as ImageDrawType
from PIL.ImageFont import FreeTypeFont

_IMAGE_PATH: str = os.path.dirname(os.path.realpath(__file__)) + "/image.jpg"
_COLOR_TEXT: str = "black"
_COLOR_OUTLINE: str = "gray"
_COLOR_BACKGROUND: str = "white"


def get_size(txt: str, font: FreeTypeFont) -> tuple[int, int]:
    """
    Get the size (height, width) of the text provided based on the font in píxels
    """
    test_img: ImageType = Image.new("RGB", (1, 1))
    test_draw: ImageDrawType = ImageDraw.Draw(test_img)
    size: tuple[int, int] = test_draw.textsize(txt, font)
    return size


def create_match_image(
    week_otter_pairs: list[tuple[User | Member, User | Member]],
) -> tuple[ImageType, str]:
    """
    Create a jpg image with the pairs of participants
    """
    first_list, second_list = zip(*week_otter_pairs)
    first_column: str = "\n".join(
        list(map(lambda user: f"{user.display_name}#{user.discriminator}", first_list)),
    )
    second_column: str = "\n".join(
        list(
            map(lambda user: f"{user.display_name}#{user.discriminator}", second_list),
        ),
    )

    # TODO: except image creation errors
    fontsize: int = 16
    font: FreeTypeFont = ImageFont.truetype(FONT_PATH, fontsize)

    width, height = get_size(first_column, font)
    width2, _height2 = get_size(second_column, font)
    img: ImageType = Image.new(
        "RGB",
        ((width + width2) + 100, (height) + 20),
        _COLOR_BACKGROUND,
    )
    image_canvas: ImageDrawType = ImageDraw.Draw(img)
    image_canvas.text((5, 5), first_column, fill=_COLOR_TEXT, font=font)
    image_canvas.text((width + 55, 5), second_column, fill=_COLOR_TEXT, font=font)
    image_canvas.rectangle((0, 0, width + 50, height + 20), outline=_COLOR_OUTLINE)
    image_canvas.rectangle(
        (width + 50, 0, (width + width2) + 100, height + 20),
        outline=_COLOR_OUTLINE,
    )

    img.save(_IMAGE_PATH)

    return img, _IMAGE_PATH
