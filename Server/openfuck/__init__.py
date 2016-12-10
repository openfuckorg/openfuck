"""
Library for running the OpenFUCK sex robot.
"""

from collections.abc import Sequence

import attr


__author__ = "riggs"


@attr.s
class Stroke:
    @staticmethod
    def _percentage_validator(instance, attriubute, value):
        if not (0 <= value <= 1):
            raise ValueError("Value must be between 0 and 1 (inclusive).")

    position = attr.ib(validator=_percentage_validator)
    velocity = attr.ib(validator=_percentage_validator)  # May be some sort of curve in the future.


@attr.s
class Pattern:
    @staticmethod
    def _actions_validator(instance, attribute, value):
        if not isinstance(value, Sequence) or \
           not all([isinstance(obj, (Stroke, Pattern)) for obj in value]):
            raise ValueError("Actions must be a sequence of Strokes or Patterns.")

    repeat = attr.ib(validator=lambda x: x >= 0)
    actions = attr.ib(validator=_actions_validator)
