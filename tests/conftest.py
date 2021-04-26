import argparse
import subprocess
from functools import reduce
from typing import Any, List, Tuple

import pytest


def assert_ip175g_command_is_correct_type(
        *,
        data: Any,
) -> None:
    assert len(data) > 0
    assert len(data[0]) == 4
    assert isinstance(data, list)
    assert isinstance(data[0], list)
    assert isinstance(data[0][0], int)


def get_data_from_cli_args(
    *,
    parser: argparse.ArgumentParser,
    args: List[str],
) -> List[List[int]]:
    parsed_args = parser.parse_args(args)
    config = parsed_args.execute(parsed_args)
    return config.create_configuration()


def run_command_to_error(
    *args: Tuple[List[str], ...],
) -> None:
    command: List[str] = reduce(lambda command, arg: command + arg, args)
    cli_status_code: int = subprocess.call(command)
    assert cli_status_code > 0, 'The command did not exit with an error code'