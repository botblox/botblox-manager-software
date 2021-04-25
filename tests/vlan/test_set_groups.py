import subprocess
from argparse import ArgumentParser
from functools import reduce
from typing import (
    Any,
    List,
    Tuple,
)


class TestSetGroups:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'usb_usart_converter_device',
        'vlan',
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

    def test_2x2_groups_1_isolated(
        self,
        parser: ArgumentParser,
    ) -> None:
        args = self.base_args + [
            '--group',
            '1',
            '2',
            '--group',
            '3',
            '4',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=args)
        self._assert_data_is_correct_type(data=data)

        expected_result = [[23, 16, 12, 12], [23, 17, 80, 0], [23, 18, 80, 255]]
        assert data == expected_result

    def test_single_port_vlan_groups(
        self,
        parser: ArgumentParser,
    ) -> None:
        args = self.base_args + [
            '--group',
            '1',
            '--group',
            '2',
            '--group',
            '3',
            '--group',
            '4',
            '--group',
            '5',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=args)
        self._assert_data_is_correct_type(data=data)

        expected_result = [[23, 16, 4, 8], [23, 17, 16, 0], [23, 18, 64, 128]]
        assert data == expected_result
