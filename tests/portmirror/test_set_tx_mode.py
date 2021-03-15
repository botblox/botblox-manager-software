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
    def _assert_data_is_correct_type(
        *,
        data: Any,
    ) -> None:
        assert len(data) > 0
        assert len(data[0]) == 4
        assert isinstance(data, list)
        assert isinstance(data[0], list)
        assert isinstance(data[0][0], int)

    @staticmethod
    def _get_data_from_cli_args(
        *,
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
        test_args = self.base_args + [
            '-M',
            '1',
            '-tx',
            '2',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=test_args)
        self._assert_data_is_correct_type(data=data)

        expected_result = [[20, 4, 8, 64], [20, 3, 1, 160]]
        assert data == expected_result

    def test_multiple_tx_port(
        self,
        parser: ArgumentParser,
    ) -> None:
        test_args = self.base_args + [
            '-M',
            '1',
            '--tx-port',
            '2',
            '3',
            '4',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=test_args)
        self._assert_data_is_correct_type(data=data)

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

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'botblox mirror: error: the following arguments are required: -tx/--tx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_default_mirror_port(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args: List[str] = [
            '--tx-port',
            '1',
            '2',
            '3',
            '4',
        ]

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureResult[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_result = [[20, 4, 92, 224], [20, 3, 1, 160]]
        actual_stderr: str = captured.err

        assert actual_stderr.find(str(expected_result)) > -1

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

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureResult[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'botblox mirror: error: the following arguments are required: -tx/--tx-port'
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

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: pytest.CaptureFixture = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'botblox: error: unrecognized arguments: 2'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
