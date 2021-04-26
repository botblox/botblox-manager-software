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

    def test_all_ports(self):
        args = self.base_args + [
            '--default-vlan',
            '20',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 7, 20, 0],  # VLAN_INFO_0
            [23, 8, 20, 0],  # VLAN_INFO_1
            [23, 9, 20, 0],  # VLAN_INFO_2
            [23, 11, 20, 0],  # VLAN_INFO_3
            [23, 12, 20, 0],  # VLAN_INFO_4
        ]
        assert data == expected_result

    def test_port_only(self):
        args = self.base_args + [
            '--port-default-vlan',
            '2',
            '20',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 8, 20, 0],  # VLAN_INFO_1
        ]
        assert data == expected_result

    def test_mixed(self):
        args = self.base_args + [
            '--default-vlan',
            '20',
            '--port-default-vlan',
            '2',
            '21'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 7, 20, 0],  # VLAN_INFO_0
            [23, 8, 21, 0],  # VLAN_INFO_1
            [23, 9, 20, 0],  # VLAN_INFO_2
            [23, 11, 20, 0],  # VLAN_INFO_3
            [23, 12, 20, 0],  # VLAN_INFO_4
        ]
        assert data == expected_result

    def test_all_ports_wrong_type(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--default-vlan',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -D/--default-vlan: invalid VLAN ID(0,4096) value: 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_all_ports_wrong_num(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--default-vlan',
            '5000',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -D/--default-vlan: invalid VLAN ID(0,4096) value: '5000'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_all_ports_missing_arg(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--default-vlan',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -D/--default-vlan: expected one argument"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port(self):
        args = self.base_args + [
            '--port-default-vlan',
            '2',
            '20',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 8, 20, 0],  # VLAN_INFO_1
        ]
        assert data == expected_result

    def test_ports(self):
        args = self.base_args + [
            '--port-default-vlan',
            '2',
            '20',
            '--port-default-vlan',
            '1',
            '21',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 7, 21, 0],  # VLAN_INFO_0
            [23, 8, 20, 0],  # VLAN_INFO_1
        ]
        assert data == expected_result

    def test_port_wrong_port_type(
            self,
            capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-default-vlan',
            'a',
            '20',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'botblox tag-vlan: error: argument -d/--port-default-vlan: ' \
                                  'Error in argument "port{1,2,3,4,5}": Invalid port \'a\''
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_wrong_port_num(
            self,
            capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-default-vlan',
            '6',
            '20',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'botblox tag-vlan: error: argument -d/--port-default-vlan: Error in argument "port{1,2,3,4,5}": Invalid port \'6\''
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_missing_vlan_arg(
            self,
            capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-default-vlan',
            '1',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -d/--port-default-vlan: expected 2 arguments"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_missing_both_args(
            self,
            capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-default-vlan',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -d/--port-default-vlan: expected 2 arguments"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
