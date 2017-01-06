"""
Library for running the OpenFUCK sex robot.
"""

import json
from collections.abc import Sequence

__author__ = "riggs"

__all__ = ("Stroke", "Wait", "Pattern", "serialize", "deserialize")


def repr_params(dict_):
    return ', '.join("{}={}".format(key, repr(value)) for key, value in dict_.items())


class Serialized:
    def __eq__(self, other):
        if isinstance(other, self.__class__) and \
                        self.to_dict() == other.to_dict():
            return True
        else:
            return False

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr_params(self.__dict__))

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, dict_):
        if cls not in (Serialized, Motion):  # Not overwritten in subclass
            raise NotImplementedError
        for klass in cls.__subclasses__():
            try:
                return klass.from_dict(dict_)
            except TypeError:
                pass
        else:
            raise TypeError("data does not match any subclasses of {}".format(cls.__name__))

    def serialize(self):
        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, data):
        return cls.from_dict(json.loads(data))


class Motion(Serialized):
    pass


class Stroke(Motion):
    def __init__(self, position, speed):
        self.position = self._validate(position)
        self.speed = self._validate(speed)

    @staticmethod
    def _validate(value):
        if not (0 <= value <= 1):
            raise ValueError("value must be between 0 and 1 (inclusive).")
        return value

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)


class Wait(Motion):
    def __init__(self, duration):
        self.duration = self._validate(duration)

    @staticmethod
    def _validate(value):
        if not (0 < value < float('inf')):
            raise ValueError("wait time must be between 0 and infinity")
        return value

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)


class Pattern(Motion):
    """
    Patterns are a sequence of Motions or Patterns that repeat a given number of times.
    """
    class Iterator:
        """
        Create a depth-first iterator of a given pattern.

        Recursively creates nested iterators of sub-patterns as appropriate.
        """
        def __init__(self, pattern):
            self.cycles = pattern.cycles
            self.motions = pattern.motions
            self.iterator = None
            self._cycle_count = 1
            self._motions_index = 0

        def __next__(self):
            if self._motions_index >= len(self.motions):    # Reached the end of the sequence, loop around.
                self._cycle_count += 1
                self._motions_index = 0
            if self._cycle_count > self.cycles:
                raise StopIteration
            if self.iterator is None:   # Not currently in a nested iterator.
                motion = self.motions[self._motions_index]
                if getattr(motion, '__iter__', None) is None:
                    self._motions_index += 1
                    return motion
                else:
                    self.iterator = iter(motion)
            try:
                return self.iterator.__next__()
            except StopIteration:
                self.iterator = None
                self._motions_index += 1
                return self.__next__()

    def __init__(self, cycles, motions):
        self.cycles = self._validate_cycles(cycles)
        self.motions = self._validate_motions(motions)

    @staticmethod
    def _validate_cycles(cycles):
        if not isinstance(cycles, int):
            try:
                cycles = float(cycles)
                cycles = int(cycles) if cycles != float('Infinity') else cycles
            except ValueError:
                raise ValueError("cycles must be a positive integer or Infinity")
        if not cycles >= 0:
            raise ValueError("cycles must be a positive integer or Infinity")
        return cycles

    @staticmethod
    def _validate_motions(motions, motion_classes=tuple(Motion.__subclasses__())):
        if not isinstance(motions, Sequence) or \
                not len(motions) or \
                not all([isinstance(obj, motion_classes) for obj in motions]):
            raise ValueError("motions must be a sequence of {} objects".format(
                                                            ', '.join(cls.__name__ for cls in motion_classes)))
        return tuple(motions)

    def __iter__(self):
        return self.Iterator(self)

    def to_dict(self):
        return {'cycles': self.cycles, 'motions': [motion.to_dict() for motion in self.motions]}

    @classmethod
    def from_dict(cls, dict_):
        try:
            dict_['motions'] = [Serialized.from_dict(motion) for motion in dict_['motions']]
        except KeyError:
            raise TypeError("missing keyword argument 'motions'")
        return cls(**dict_)


class Query(Serialized):
    def __init__(self, pattern=False, stroke=False):
        self.pattern = pattern
        self.stroke = stroke

    def to_dict(self):
        return dict((key, value.to_dict() if hasattr(value, 'to_dict') else value)
                    for key, value in self.__dict__.items())

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)


def serialize(obj):
    if hasattr(obj, 'serialize'):
        raise TypeError("invalid type: {}".format(type(obj)))
    return obj.serialize()


def deserialize(data):
    return Serialized.deserialize(data)
