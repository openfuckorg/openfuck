"""
Library for running the OpenFUCK sex robot.
"""

import attr
import json
from collections.abc import Sequence


__author__ = "riggs"


@attr.s
class Stroke:
    @staticmethod
    def _percentage_validator(instance, attriubute, value):
        if not (0 <= value <= 1):
            raise ValueError("Value must be between 0 and 1 (inclusive).")

    position = attr.ib(validator=_percentage_validator)
    velocity = attr.ib(validator=_percentage_validator)  # May be some sort of curve in the future.

    def _to_json(self):
        return json.dumps(attr.asdict(self))

    @classmethod
    def _from_json(cls, data):
        return json.loads(data, object_hook=lambda obj: cls(**obj))

    serialize = _to_json
    deserialize = _from_json


@attr.s
class Pattern:
    @staticmethod
    def _actions_validator(instance, attribute, value):
        if not isinstance(value, Sequence) or \
           not all([isinstance(obj, (Stroke, Pattern)) for obj in value]):
            raise ValueError("Actions must be a sequence of Strokes or Patterns.")

    repeat = attr.ib(validator=lambda x: x >= 0)
    actions = attr.ib(validator=_actions_validator)

    def _to_json(self):
        return json.dumps(attr.asdict(self))

    @classmethod
    def _from_json(cls, data):
        if 'repeat' in data:
            return json.loads(data, object_hook=lambda obj: cls(**obj))
        else:
            return json.loads(data, object_hook=lambda obj: Stroke(**obj))

    serialize = _to_json
    deserialize = _from_json
