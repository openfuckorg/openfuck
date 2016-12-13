import logging
import sys

__author__ = "riggs"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)


def logger(name):
    return logging.getLogger(name)
