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

from botblox_config.cli import create_parser

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args, run_command_to_error


class TestSetTxMode:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'mirror',
        '-m',
        'TX',
    ]

    def test_single_tx_port(
        self,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '-tx',
            '2',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 8, 64], [20, 3, 1, 160]]
        assert data == expected_result

    def test_multiple_tx_port(
        self,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '--tx-port',
            '2',
            '3',
            '4',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 88, 64], [20, 3, 1, 160]]
        assert data == expected_result

    def test_no_tx_port(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'mirror: error: the following arguments are required: -tx/--tx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_default_mirror_port(
        self,
    ) -> None:
        test_args = self.base_args + [
            '--tx-port',
            '1',
            '2',
            '3',
            '4',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 92, 224], [20, 3, 1, 160]]
        assert data == expected_result

    def test_single_rx_port(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args: List[str] = [
            '-M',
            '1',
            '--rx-port',
            '2'
        ]

        run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureResult[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'mirror: error: the following arguments are required: -tx/--tx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_multiple_mirror_ports(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args: List[str] = [
            '-M',
            '1',
            '2',
            '-tx',
            '3',
            '4',
        ]

        run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureFixture = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'error: unrecognized arguments: 2'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
