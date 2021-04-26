from typing import List, AnyStr
from pytest import CaptureFixture

from botblox_config.cli import create_parser

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args, run_command_to_error


class TestSetGroups:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'tag-vlan',
    ]

    def test_vlan_one_member(self):
        args = self.base_args + [
            '--vlan',
            '2',
            '1',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [24, 0, 1, 0],  # VLAN_VALID
            [24, 1, 2, 0],  # VID_0
            [24, 17, 0b00000100, 255],  # VLAN_MEMBER_0
        ]
        assert data == expected_result

    def test_vlan_two_members(self):
        args = self.base_args + [
            '--vlan',
            '2',
            '1',
            '4',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [24, 0, 1, 0],  # VLAN_VALID
            [24, 1, 2, 0],  # VID_0
            [24, 17, 0b01000100, 255],  # VLAN_MEMBER_0
        ]
        assert data == expected_result

    def test_vlan_two_vlans(self):
        args = self.base_args + [
            '--vlan',
            '2',
            '1',
            '4',
            '--vlan',
            '20',
            '2',
            '4',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [24, 0, 1 << 1, 0],  # VLAN_VALID
            [24, 1, 2, 0],  # VID_0
            [24, 2, 20, 0],  # VID_1
            [24, 17, 0b01000100, 0b01001000],  # VLAN_MEMBER_0, VLAN_MEMBER_1
        ]
        assert data == expected_result

    def test_vlan_three_vlans(self):
        args = self.base_args + [
            '--vlan',
            '2',
            '1',
            '4',
            '--vlan',
            '20',
            '2',
            '4',
            '--vlan',
            '21',
            '2',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [24, 0, 1 << 2, 0],  # VLAN_VALID
            [24, 1, 2, 0],  # VID_0
            [24, 2, 20, 0],  # VID_1
            [24, 3, 21, 0],  # VID_2
            [24, 17, 0b01000100, 0b01001000],  # VLAN_MEMBER_0, VLAN_MEMBER_1
            [24, 18, 0b00001000, 255],  # VLAN_MEMBER_2
        ]
        assert data == expected_result

    def test_wrong_vlan_type(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan',
            'WRONG',
            '1'
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: Wrong VLAN ID."
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_wrong_vlan(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan',
            '5000',
            '1'
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: VLAN ID 5000 is invalid for Switchblox with max VLAN ID 4096"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_wrong_port_type(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan',
            '2',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: Invalid port 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_wrong_port(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan',
            '2',
            '6',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: Invalid port '6'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_vlan_no_args(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -v/--vlan: expected at least one argument"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_vlan_too_many(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = list(self.base_args)
        for i in range(17):
            test_args += [
                '--vlan', str(i), '1',
            ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: Too many VLAN table entries specified. Maximum is 16"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
