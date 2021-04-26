from typing import List, AnyStr
from pytest import CaptureFixture

from manager.cli import create_parser

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args, run_command_to_error


class TestSetGroups:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'tag-vlan',
    ]

    def test_two_port_vlan(self):
        args = self.base_args + [
            '-d', '1', '2',
            '-d', '4', '2',
            '-M', 'OPTIONAL',
            '-a', '1', 'ADD',
            '-a', '4', 'STRIP',
            '-v', '2', '1', '4'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 32],  # UNVID_MODE
            [23, 1, 220, 0],  # TAG_VLAN_EN
            [23, 7, 2, 0],  # VLAN_INFO_0
            [23, 11, 2, 0],  # VLAN_INFO_3
            [23, 13, 4, 0],  # ADD_TAG
            [23, 14, 64, 0],  # REMOVE_TAG
            [24, 0, 1, 0],  # VLAN_VALID
            [24, 1, 2, 0],  # VID_0
            [24, 17, 68, 255]  # VLAN_MEMBER_0
        ]
        assert data == expected_result
