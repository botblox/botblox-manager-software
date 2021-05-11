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

    def test_force_all(self) -> None:
        args = self.base_args + [
            '--force-vlan-id',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 1, 0, 0b11011100],  # VLAN_CLS
        ]
        assert data == expected_result

    def test_force_one(self) -> None:
        args = self.base_args + [
            '--force-vlan-id',
            '2',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 1, 0, 0b00001000],  # VLAN_CLS
        ]
        assert data == expected_result

    def test_force_two(self) -> None:
        args = self.base_args + [
            '--force-vlan-id',
            '2',
            '5',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 1, 0, 0b10001000],  # VLAN_CLS
        ]
        assert data == expected_result

    def test_force_one_wrong(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--force-vlan-id',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -f/--force-vlan-id: invalid port value: 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_force_next_wrong(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--force-vlan-id',
            '1',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -f/--force-vlan-id: invalid port value: 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_force_wrong_port_nr(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--force-vlan-id',
            '6',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "tag-vlan: error: argument -f/--force-vlan-id: invalid port value: '6'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
