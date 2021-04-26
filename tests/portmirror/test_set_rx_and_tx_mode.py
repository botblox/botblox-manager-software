import subprocess
from argparse import ArgumentParser
from functools import reduce
from typing import Any, AnyStr, List, Tuple

from pytest import CaptureFixture

from manager.cli import create_parser


class TestSetRxAndTxMode:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'usb_usart_converter_device',
        'mirror',
        '-m',
        'RXandTX',
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

        data = self._get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        self._assert_data_is_correct_type(data=data)

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

        data = self._get_data_from_cli_args(parser=create_parser(self.base_args), args=test_args)
        self._assert_data_is_correct_type(data=data)

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

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr = 'botblox mirror: error: the following arguments are required: -rx/--rx-port'
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

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr = 'botblox mirror: error: the following arguments are required: -tx/--tx-port'
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

        self._run_command_to_error(self.package, self.base_args, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr = 'botblox mirror: error: the following arguments are required: -rx/--rx-port, -tx/--tx-port'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr) > -1
