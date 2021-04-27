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

    def test_mode_disabled(self) -> None:
        args = self.base_args + [
            '--vlan-mode',
            'DISABLED',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 32],  # UNVID_MODE=1
            [23, 1, 0, 0],  # TAG_VLAN_EN
        ]
        assert data == expected_result

    def test_mode_optional(self) -> None:
        args = self.base_args + [
            '--vlan-mode',
            'OPTIONAL',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 32],  # UNVID_MODE=1
            [23, 1, 0b11011100, 0],  # TAG_VLAN_EN
        ]
        assert data == expected_result

    def test_mode_enabled(self) -> None:
        args = self.base_args + [
            '--vlan-mode',
            'ENABLED',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 0],  # UNVID_MODE=0
            [23, 1, 0b11011100, 0],  # TAG_VLAN_EN
            [23, 2, 0b00100011, 0b00000100],  # VLAN_INGRESS_FILTER
        ]
        assert data == expected_result

    def test_mode_strict(self) -> None:
        args = self.base_args + [
            '--vlan-mode',
            'STRICT',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 0],  # UNVID_MODE=0
            [23, 1, 0b11011100, 0],  # TAG_VLAN_EN
            [23, 2, 255, 0b00000100],  # VLAN_INGRESS_FILTER
        ]
        assert data == expected_result

    def test_mode_wrong(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan-mode',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -M/--vlan-mode: invalid VLANMode value: 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_mode_missing_arg(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--vlan-mode',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -M/--vlan-mode: expected one argument"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_disabled(self) -> None:
        args = self.base_args + [
            '--port-vlan-mode',
            '2',
            'DISABLED',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 32],  # UNVID_MODE=1
            [23, 1, 0, 0],  # TAG_VLAN_EN
        ]
        assert data == expected_result

    def test_port_mode_optional(self) -> None:
        args = self.base_args + [
            '--port-vlan-mode',
            '2',
            'OPTIONAL',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 32],  # UNVID_MODE=1
            [23, 1, 0b00001000, 0],  # TAG_VLAN_EN
        ]
        assert data == expected_result

    def test_port_mode_enabled(self) -> None:
        args = self.base_args + [
            '--port-vlan-mode',
            '2',
            'ENABLED',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 0],  # UNVID_MODE=0
            [23, 1, 0b00001000, 0],  # TAG_VLAN_EN
            [23, 2, 0b11110111, 0b00000100],  # VLAN_INGRESS_FILTER
        ]
        assert data == expected_result

    def test_port_mode_strict(self) -> None:
        args = self.base_args + [
            '--port-vlan-mode',
            '2',
            'STRICT',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 0],  # UNVID_MODE=0
            [23, 1, 0b00001000, 0],  # TAG_VLAN_EN
            [23, 2, 0b11111111, 0b00000100],  # VLAN_INGRESS_FILTER
        ]
        assert data == expected_result

    def test_port_mode_wrong_mode(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-mode',
            '1',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'tag-vlan: error: argument -m/--port-vlan-mode: Wrong value "WRONG" of ' \
                                  'argument "vlan_mode", allowed values are {DISABLED,OPTIONAL,ENABLED,STRICT}'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_wrong_port_type(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-mode',
            'a',
            'OPTIONAL',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'tag-vlan: error: argument -m/--port-vlan-mode: ' \
                                  'Error in argument "port{1,2,3,4,5}": Invalid port \'a\''
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_wrong_port_num(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-mode',
            '6',
            'OPTIONAL',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'tag-vlan: error: argument -m/--port-vlan-mode: ' \
                                  'Error in argument "port{1,2,3,4,5}": Invalid port \'6\''
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_missing_mode_arg(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-mode',
            '1',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -m/--port-vlan-mode: expected 2 arguments"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_missing_both_args(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-mode',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -m/--port-vlan-mode: expected 2 arguments"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_two_ports_enabled(self) -> None:
        args = self.base_args + [
            '--port-vlan-mode',
            '2',
            'ENABLED',
            '--port-vlan-mode',
            '1',
            'ENABLED'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 0],  # UNVID_MODE=0
            [23, 1, 0b00001100, 0],  # TAG_VLAN_EN
            [23, 2, 0b11110011, 0b00000100],  # VLAN_INGRESS_FILTER
        ]
        assert data == expected_result

    def test_port_mode_two_ports_impossible(
            self,
            capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-vlan-mode',
            '2',
            'ENABLED',
            '--port-vlan-mode',
            '1',
            'OPTIONAL'
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: Switchblox can only have all its ports in mode DISABLED/OPTIONAL " \
                                  "or all in ENABLED/STRICT, but not a combination of these two groups."
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_with_default(self) -> None:
        args = self.base_args + [
            '--vlan-mode',
            'ENABLED',
            '--port-vlan-mode',
            '1',
            'STRICT'
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 0, 0, 0],  # UNVID_MODE=0
            [23, 1, 0b11011100, 0],  # TAG_VLAN_EN
            [23, 2, 0b00100111, 0b00000100],  # VLAN_INGRESS_FILTER
        ]
        assert data == expected_result
