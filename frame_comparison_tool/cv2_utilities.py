from typing import Tuple
from enum import Enum

import cv2


class Align(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


_FONT_FACE = 2
_FONT_SCALE = 1.0
_COLOR = (255, 255, 255)
_THICKNESS = 3
_BORDER_COLOR = (0, 0, 0)
_BORDER_THICKNESS = 2
_ALIGN = Align.LEFT


def get_text_size(text: str,
                  font_face: int = _FONT_FACE,
                  font_scale: float = _FONT_SCALE,
                  thickness: int = _THICKNESS) -> Tuple[int, int]:
    size, _ = cv2.getTextSize(text=text, fontFace=font_face, fontScale=font_scale, thickness=thickness)
    width, height = size

    return width, height


def put_bordered_text(img: cv2.typing.MatLike,
                      text: str,
                      org: cv2.typing.Point,
                      align: Align = _ALIGN,
                      font_face: int = _FONT_FACE,
                      font_scale: float = _FONT_SCALE,
                      color: cv2.typing.Scalar = _COLOR,
                      thickness: int = _THICKNESS,
                      border_color: cv2.typing.Scalar = _BORDER_COLOR,
                      border_thickness: int = _BORDER_THICKNESS) -> cv2.typing.MatLike:
    text_width, text_height = get_text_size(text=text, font_face=font_face, font_scale=font_scale, thickness=thickness)

    org = (org[0], org[1] + text_height)

    img = cv2.putText(img=img, text=text, org=org, fontFace=font_face, fontScale=font_scale,
                      color=border_color, thickness=thickness)

    img = cv2.putText(img=img, text=text, org=org, fontFace=font_face, fontScale=font_scale,
                      color=color, thickness=thickness - border_thickness)

    return img
