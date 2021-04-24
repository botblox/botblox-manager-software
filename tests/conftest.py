import argparse

import pytest
from botblox_config.cli import create_parser


@pytest.fixture(scope='function')
def parser() -> argparse.ArgumentParser:
    return create_parser()
