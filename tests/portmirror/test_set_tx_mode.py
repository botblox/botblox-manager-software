import subprocess
from argparse import ArgumentParser
from functools import reduce
from typing import (
    Any,
    AnyStr,
    List,
    Tuple,
)

import pytest
from pytest import CaptureFixture


class TestSetTxMode:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'usb_usart_converter_device',
        'mirror',
        '-m',
        'TX',
    ]

    @staticmethod
    def _assert_data_is_correct_type(data: Any) -> None:
        assert len(data) > 0
        assert len(data[0]) == 4
        assert isinstance(data, list)
        assert isinstance(data[0], list)
        assert isinstance(data[0][0], int)

    @staticmethod
    def _get_data_from_cli_args(
        parser: ArgumentParser,
        args: List[str],
    ) -> List[List[int]]:
        parsed_args = parser.parse_args(args)
        config = parsed_args.execute(parsed_args)
        return config.create_configuration()

    @staticmethod
    def _run_command_to_error(
        *args: Tuple[List[str], ...],
    ) -> None:
        command: List[str] = reduce(lambda command, arg: command + arg, args)
        cli_status_code: int = subprocess.call(command)
        assert cli_status_code > 0, 'The command did not exit with an error code'

    def test_single_tx_port(
        self,
        parser: ArgumentParser,
    ) -> None:
        args = self.base_args + [
            '-M',
            '1',
            '-tx',
            '2',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=args)
        self._assert_data_is_correct_type(data=data)

        expected_result = [[20, 4, 8, 64], [20, 3, 1, 160]]
        assert data == expected_result
