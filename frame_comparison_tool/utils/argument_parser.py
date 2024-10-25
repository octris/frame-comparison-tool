import argparse
from argparse import Namespace
from frame_comparison_tool.utils.frame_type import FrameType


# TODO: Check choices in frame type

def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', type=str, nargs='*', required=False)
    parser.add_argument('--n-samples', type=int, required=False, default=5)
    parser.add_argument('--seed', type=int, required=False, default=42)
    parser.add_argument('--frame-type', type=FrameType, choices=list(FrameType), required=False,
                        default="B-Type")

    return parser.parse_args()
