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

    def test_mode_any(self):
        args = self.base_args + [
            '--receive-mode',
            'ANY',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 2, 255, 0b0000_0100],  # ACCEPTABLE_FRM_TYPE
        ]
        assert data == expected_result

    def test_mode_only_tagged(self):
        args = self.base_args + [
            '--receive-mode',
            'ONLY_TAGGED',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 2, 255, 0b0000_0101],  # ACCEPTABLE_FRM_TYPE
        ]
        assert data == expected_result

    def test_mode_only_untagged(self):
        args = self.base_args + [
            '--receive-mode',
            'ONLY_UNTAGGED',
        ]

        data = get_data_from_cli_args(parser=create_parser(args), args=args)
        assert_ip175g_command_is_correct_type(data=data)

        expected_result = [
            [23, 2, 255, 0b0000_0110],  # ACCEPTABLE_FRM_TYPE
        ]
        assert data == expected_result

    def test_mode_wrong(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--receive-mode',
            'WRONG',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -T/--receive-mode: invalid VLANReceiveMode value: 'WRONG'"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_mode_missing_arg(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--receive-mode',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = "botblox tag-vlan: error: argument -T/--receive-mode: expected one argument"
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1

    def test_port_mode_unavailable(
        self,
        capfd: CaptureFixture,
    ) -> None:
        test_args = self.base_args + [
            '--port-receive-mode',
            '1',
            'ANY',
        ]

        run_command_to_error(self.package, test_args)

        captured: CaptureFixture[AnyStr] = capfd.readouterr()
        assert captured.out == ''

        expected_stderr_message = 'error: unrecognized arguments: --port-receive-mode 1 ANY'
        actual_stderr: str = captured.err

        assert actual_stderr.find(expected_stderr_message) > -1
