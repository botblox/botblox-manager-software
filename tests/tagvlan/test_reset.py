from typing import List

from botblox_config.cli import create_parser

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args


class TestSetReset:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        '--switch',
        'switchblox',
        'tag-vlan',
        '--reset',
    ]

    def test_reset(self) -> None:
        data = get_data_from_cli_args(
            parser=create_parser(self.base_args),
            args=self.base_args,
        )
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 160],  # UNVID_MODE=1, VLAN_TABLE_CLR=1
            [23, 1, 0, 0],  # TAG_VLAN_EN=0
            [23, 2, 255, 4],  # ACCEPTABLE_FRM_TYPE=0
            [23, 13, 0, 0],  # ADD_TAG=0
            [23, 14, 0, 0],  # REMOVE_TAG=0
            [24, 0, 0, 0]  # VLAN_VALID=0
        ]
        assert data == expected_result
