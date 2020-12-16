"""Module adding CLI subparsers together."""

import datetime
import logging

logging.basicConfig(level=logging.DEBUG)


def test() -> datetime.datetime:
    """The test function's docstring."""
    return datetime.datetime.utcnow()
