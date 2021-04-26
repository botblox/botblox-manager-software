import subprocess
from argparse import ArgumentParser
from functools import reduce
from typing import (
    Any,
    List,
    Tuple,
)

from botblox_config.cli import create_parser

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args

class TestSetGroups:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'vlan',
    ]

    def test_2x2_groups_1_isolated(
        self,
    ) -> None:
        args = self.base_args + [
            '--group',
            '1',
            '2',
            '--group',
            '3',
            '4',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[23, 16, 12, 12], [23, 17, 80, 0], [23, 18, 80, 255]]
        assert data == expected_result
