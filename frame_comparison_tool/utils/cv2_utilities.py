from typing import Tuple
import cv2

from frame_comparison_tool.utils.align import Align
from frame_comparison_tool.utils.exceptions import InvalidAlignmentError

_FONT_FACE = 2
_FONT_SCALE = 0.85
_COLOR = (255, 255, 255)
_THICKNESS = 3
_BORDER_COLOR = (0, 0, 0)
_BORDER_THICKNESS = 2
_ALIGN = Align.LEFT


def get_text_size(text: str,
                  font_face: int,
                  font_scale: float,
                  thickness: int) -> Tuple[int, int]:
    size, baseline = cv2.getTextSize(text=text, fontFace=font_face, fontScale=font_scale, thickness=thickness)
    width, height = size
    height += baseline

    return width, height


def put_bordered_text(img: cv2.typing.MatLike,
                      text: str,
                      origin: cv2.typing.Point,
                      align: Align = _ALIGN,
                      font_face: int = _FONT_FACE,
                      font_scale: float = _FONT_SCALE,
                      color: cv2.typing.Scalar = _COLOR,
                      thickness: int = _THICKNESS,
                      border_color: cv2.typing.Scalar = _BORDER_COLOR,
                      border_thickness: int = _BORDER_THICKNESS) -> cv2.typing.MatLike:
    y_offset = origin[1]

    for line in text.splitlines():
        text_width, text_height = get_text_size(text=line, font_face=font_face, font_scale=font_scale,
                                                thickness=thickness)

        x_offset = origin[0]
        y_offset += text_height

        if align == Align.LEFT:
            pass
        elif align == Align.CENTER:
            x_offset -= int(text_width / 2)
        elif align == Align.RIGHT:
            x_offset -= text_width
        else:
            raise InvalidAlignmentError(align)

        img = cv2.putText(img=img, text=line, org=(x_offset, y_offset), fontFace=font_face, fontScale=font_scale,
                          color=border_color, thickness=thickness)

        img = cv2.putText(img=img, text=line, org=(x_offset, y_offset), fontFace=font_face, fontScale=font_scale,
                          color=color, thickness=thickness - border_thickness)

    return img
