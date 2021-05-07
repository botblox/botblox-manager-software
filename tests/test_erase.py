from typing import List

from botblox_config.cli import create_parser

from .conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args


class TestErase:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'erase',
    ]

    def test_erase(
        self,
    ) -> None:
        data = get_data_from_cli_args(
            parser=create_parser(self.base_args),
            args=self.base_args,
        )
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [[101, 0, 0, 0]]
        assert data == expected_result
