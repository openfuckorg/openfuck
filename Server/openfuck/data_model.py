"""
Library for running the OpenFUCK sex robot.
"""

import attr
import json
from collections.abc import Sequence


__author__ = "riggs"
__all__ = ('Stroke', 'Pattern')


class Serializer:

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, dict_):
        if cls is not Serializer:   # Not overwritten in subclass
            raise NotImplementedError
        for klass in cls.__subclasses__():
            try:
                return klass.from_dict(dict_)
            except TypeError:
                pass
        else:
            raise TypeError("dictionary does not match any subclasses of", cls.__name__)

    def serialize(self):
        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, data):
        return cls.from_dict(json.loads(data))


@attr.s
class Stroke(Serializer):

    def _percentage_validator(self, attriubute, value):
        if not (0 <= value <= 1):
            raise ValueError("value must be between 0 and 1 (inclusive).")

    position = attr.ib(validator=_percentage_validator)
    velocity = attr.ib(validator=_percentage_validator)  # May be some sort of curve in the future.

    def to_dict(self):
        return attr.asdict(self)

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)


@attr.s
class Pattern(Serializer):

    def _actions_validator(self, attribute, value):
        if not isinstance(value, Sequence) or \
                not len(value) or \
                not all([isinstance(obj, (Stroke, Pattern)) for obj in value]):
            raise ValueError("actions must be a sequence of Strokes or Patterns.")

    repeat = attr.ib(convert=lambda v: v if v is not None else float('inf'), validator=lambda i, a, v: v >= 0)
    actions = attr.ib(validator=_actions_validator)

    def to_dict(self):
        return {'repeat': self.repeat, 'actions': [action.to_dict() for action in self.actions]}

    @classmethod
    def from_dict(cls, dict_):
        try:
            dict_['actions'] = [Serializer.from_dict(action) for action in dict_['actions']]
        except KeyError:
            raise TypeError("missing keyword argument 'actions'")
        return cls(**dict_)
