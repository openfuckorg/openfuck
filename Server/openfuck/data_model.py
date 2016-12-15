"""
Library for running the OpenFUCK sex robot.
"""

import json
from collections.abc import Sequence


__author__ = "riggs"
__all__ = ('Stroke', 'Pattern')


class Serializer:

    def __eq__(self, other):
        if isinstance(other, self.__class__) and \
                        self.to_dict() == other.to_dict():
            return True
        else:
            return False

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


class Stroke(Serializer):

    def __init__(self, position, speed):
        self.position = self._validate(position)
        self.speed = self._validate(speed)

    @staticmethod
    def _validate(value):
        if not (0 <= value <= 1):
            raise ValueError("value must be between 0 and 1 (inclusive).")
        return value

    def __repr__(self):
        return "{}(position={}, speed={}".format(self.__class__.__name__, self.position, self.speed)

    def to_dict(self):
        return {'position': self.position, 'speed': self.speed}

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)


class Pattern(Serializer):

    class Iterator:
        def __init__(self, pattern):
            self.repeat = pattern.repeat
            self.original_actions = tuple(pattern.actions)
            self.actions = list(pattern.actions)
            self._repeat_count = 0
            self._actions_index = 0

        def __next__(self):
            if self._actions_index >= len(self.actions):
                self._repeat_count += 1
                self._actions_index = 0
            if self._repeat_count > self.repeat:
                raise StopIteration
            thing = self.actions[self._actions_index]
            if isinstance(thing, Stroke):
                stroke = thing
                self._actions_index += 1
            else:
                if not getattr(thing, '__next__', None):
                    thing = self.actions[self._actions_index] = iter(thing)
                try:
                    stroke = thing.__next__()
                except StopIteration:
                    self.actions[self._actions_index] = self.original_actions[self._actions_index]
                    self._actions_index += 1
                    stroke = self.__next__()
            return stroke

    def __init__(self, repeat, actions):
        self.repeat = self._validate_repeat(repeat)
        self.actions = self._validate_actions(actions)

    @staticmethod
    def _validate_repeat(repeat):
        if repeat is None:
            repeat = float('inf')
        if not repeat >= 0:
            raise ValueError("repeat must be greater than 0")
        return repeat

    @staticmethod
    def _validate_actions(actions):
        if not isinstance(actions, Sequence) or \
                not len(actions) or \
                not all([isinstance(obj, (Stroke, Pattern)) for obj in actions]):
            raise ValueError("actions must be a sequence of Strokes or Patterns.")
        return actions

    def __repr__(self):
        return "{}(repeat={}, actions={}".format(self.__class__.__name__, self.repeat, self.actions)

    def __iter__(self):
        return self.Iterator(self)

    def to_dict(self):
        return {'repeat': self.repeat, 'actions': [action.to_dict() for action in self.actions]}

    @classmethod
    def from_dict(cls, dict_):
        try:
            dict_['actions'] = [Serializer.from_dict(action) for action in dict_['actions']]
        except KeyError:
            raise TypeError("missing keyword argument 'actions'")
        return cls(**dict_)
