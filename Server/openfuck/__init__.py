
import attr


__author__ = "riggs"


def percentage_validator(instance, attriubute, value):
    if not (0 <= value <= 1):
        raise ValueError("Value must be between 0 and 1 (inclusive).")


@attr.s
class Stroke:
    position = attr.ib(validator=percentage_validator)
    velocity = attr.ib(validator=percentage_validator)  # May be some sort of curve in the future.

