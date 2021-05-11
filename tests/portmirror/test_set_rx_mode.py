from typing import (
    AnyStr,
    List,
)

import pytest
from botblox_config.cli import create_parser
from pytest import CaptureFixture

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args, run_command_to_error


class TestSetRxMode:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'mirror',
        '-m',
        'RX',
    ]

    def test_single_rx_port(
        self,
    ) -> None:
        args = self.base_args + [
            '-M',
            '1',
            '-rx',
            '2',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 1, 64], [20, 3, 8, 128]]
        assert data == expected_result

    def test_multiple_rx_port(
        self,
    ) -> None:
        args = self.base_args + [
            '-M',
            '1',
            '-rx',
            '2',
            '3',
            '4',
            '5',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 1, 64], [20, 3, 216, 128]]
        assert data == expected_result

    def test_no_rx_port(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args: List[str] = [
            '-M',
            '1',
        ]

        run_command_to_error(self.package, self.base_args, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'mirror: error: the following arguments are required: -rx/--rx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_default_mirror_port(
        self,
    ) -> None:
        args = self.base_args + [
            '--rx-port',
            '1',
            '2',
            '3',
            '4',
        ]

        data = get_data_from_cli_args(parser=create_parser(self.base_args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[20, 4, 1, 224], [20, 3, 92, 128]]
        assert data == expected_result

    def test_single_tx_port(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args: List[str] = [
            '-M',
            '1',
            '--tx-port',
            '2'
        ]

        run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureResult[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'mirror: error: the following arguments are required: -rx/--rx-port'
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
            '-rx',
            '3',
            '4',
        ]

        run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureFixture = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'error: unrecognized arguments: 2'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
