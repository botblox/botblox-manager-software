import argparse
import subprocess
import sys
from functools import reduce
from typing import Any, List, Tuple

from botblox_config.switch import SwitchChip


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
    parser: Tuple[argparse.ArgumentParser, SwitchChip],
    args: List[str],
) -> List[List[int]]:
    parsed_args = parser[0].parse_args(args)
    config = parsed_args.execute(parsed_args)
    return config.create_configuration()


def run_command_to_error(
    *args: Tuple[List[str], ...],
) -> None:
    if len(args) > 0 and len(args[0]) > 0 and args[0][0] == "botblox":
        args = ([sys.executable, "-m", "botblox_config"],) + args[1:]
    command: List[str] = reduce(lambda comm, arg: comm + arg, args)
    cli_status_code: int = subprocess.call(command)
    assert cli_status_code > 0, 'The command did not exit with an error code'
