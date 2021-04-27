from typing import AnyStr, List

from botblox_config.cli import create_parser
from pytest import CaptureFixture

from ..conftest import assert_ip175g_command_is_correct_type, get_data_from_cli_args, run_command_to_error


class TestSetGroups:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'test',
        'tag-vlan',
    ]

    def test_action_keep(self) -> None:
        args = self.base_args + [
            '--header-action',
            'KEEP',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000000, 0],  # ADD_TAG
            [23, 14, 0b00000000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_action_add(self) -> None:
        args = self.base_args + [
            '--header-action',
            'ADD',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b11011100, 0],  # ADD_TAG
            [23, 14, 0b00000000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_action_strip(self) -> None:
        args = self.base_args + [
            '--header-action',
            'STRIP',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000000, 0],  # ADD_TAG
            [23, 14, 0b11011100, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_action_wrong(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--header-action',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -A/--header-action: " \
                                  "invalid VLANHeaderAction value: 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_action_missing_arg(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--header-action',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -A/--header-action: expected one argument"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_action_keep(self) -> None:
        args = self.base_args + [
            '--port-header-action',
            '2',
            'KEEP',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000000, 0],  # ADD_TAG
            [23, 14, 0b00000000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_port_action_add(self) -> None:
        args = self.base_args + [
            '--port-header-action',
            '2',
            'ADD',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00001000, 0],  # ADD_TAG
            [23, 14, 0b00000000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_port_action_strip(self) -> None:
        args = self.base_args + [
            '--port-header-action',
            '2',
            'STRIP',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000000, 0],  # ADD_TAG
            [23, 14, 0b00001000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_port_action_wrong_action(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-header-action',
            '1',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'tag-vlan: error: argument -a/--port-header-action: Wrong value "WRONG" of ' \
                                  'argument "header_action", allowed values are {KEEP,ADD,STRIP}'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_action_wrong_port_type(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-header-action',
            'a',
            'ADD',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'tag-vlan: error: argument -a/--port-header-action: ' \
                                  'Error in argument "port{1,2,3,4,5}": Invalid port \'a\''
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_action_wrong_port_num(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-header-action',
            '6',
            'ADD',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'tag-vlan: error: argument -a/--port-header-action: ' \
                                  'Error in argument "port{1,2,3,4,5}": Invalid port \'6\''
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_action_missing_action_arg(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-header-action',
            '1',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -a/--port-header-action: expected 2 arguments"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_action_missing_both_args(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-header-action',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -a/--port-header-action: expected 2 arguments"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_action_two_ports_strip(self) -> None:
        args = self.base_args + [
            '--port-header-action',
            '2',
            'STRIP',
            '--port-header-action',
            '1',
            'STRIP'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000000, 0],  # ADD_TAG
            [23, 14, 0b00001100, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_port_action_two_ports_mixed(self) -> None:
        args = self.base_args + [
            '--port-header-action',
            '2',
            'STRIP',
            '--port-header-action',
            '1',
            'ADD'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000100, 0],  # ADD_TAG
            [23, 14, 0b00001000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_port_action_with_default(self) -> None:
        args = self.base_args + [
            '--header-action',
            'STRIP',
            '--port-header-action',
            '1',
            'ADD'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 13, 0b00000100, 0],  # ADD_TAG
            [23, 14, 0b11011000, 0],  # REMOVE_TAG
        ]
        assert data == expected_result

    def test_port_vlan_action_unavailable(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-header-action',
            '1',
            '2',
            'KEEP',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'error: unrecognized arguments: --port-vlan-header-action 1 2 KEEP'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
