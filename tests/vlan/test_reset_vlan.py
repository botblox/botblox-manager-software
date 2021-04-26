from argparse import ArgumentParser
from typing import (Any, List)

from botblox_config.cli import create_parser

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args


class TestSetReset:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'vlan',
        '--reset',
    ]

    def test_reset(
        self,
    ) -> None:
        data = get_data_from_cli_args(
            parser=create_parser(self.base_args),
            args=self.base_args,
        )
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[23, 16, 255, 255], [23, 17, 255, 0], [23, 18, 255, 255]]
        assert data == expected_result
