import subprocess
from argparse import ArgumentParser
from functools import reduce
from typing import Any, AnyStr, List, Tuple

from pytest import CaptureFixture

from botblox_config.cli import create_parser

from ..conftest import run_command_to_error, assert_ip175g_command_is_correct_type, get_data_from_cli_args


class TestSetRxAndTxMode:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'mirror',
        '-m',
        'RXandTX',
    ]

    def test_single_tx_and_single_rx_port(
        self,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '-tx',
            '2',
            '-rx',
            '3',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 8, 64], [20, 3, 16, 192]]
        assert data == expected_result

    def test_same_tx_and_rx_port(
        self,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '-tx',
            '2',
            '-rx',
            '2',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 8, 64], [20, 3, 8, 192]]
        assert data == expected_result

    def test_rx_port_non_existent(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '-tx',
            '2',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr = 'mirror: error: the following arguments are required: -rx/--rx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr) > -1

    def test_tx_port_non_existent(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '-rx',
            '2',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr = 'mirror: error: the following arguments are required: -tx/--tx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr) > -1

    def test_no_rx_or_tx_port(
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

        expected_stderr = 'mirror: error: the following arguments are required: -rx/--rx-port, -tx/--tx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr) > -1
