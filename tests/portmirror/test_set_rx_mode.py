import argparse
from typing import Any, List

import inspect


class TestSetRxMode:
    base_args: List[str] = [
        '--device',
        'usb_usart_converter_device',
        'mirror',
        '-m',
        'RX',
    ]

    @staticmethod
    def _assert_data_is_correct_type(data: Any) -> None:
        assert len(data) > 0
        assert len(data[0]) == 4
        assert isinstance(data, list)
        assert isinstance(data[0], list)
        assert isinstance(data[0][0], int)

    @staticmethod
    def _get_data_from_cli_args(
        parser: argparse.ArgumentParser,
        args: List[str],
    ) -> List[List[int]]:
        parsed_args = parser.parse_args(args)
        config = parsed_args.execute(parsed_args)
        return config.create_configuration()

    def test_single_rx_port(self, parser: argparse.ArgumentParser) -> None:
        args = self.base_args + [
            '-M',
            '1',
            '-rx',
            '2',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=args)
        self._assert_data_is_correct_type(data=data)

        expected_result = [[20, 4, 1, 64], [20, 3, 8, 128]]
        assert data == expected_result

    def test_multiple_rx_port(self, parser: argparse.ArgumentParser) -> None:
        args = self.base_args + [
            '-M',
            '1',
            '-rx',
            '2',
            '3',
            '4',
            '5',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=args)
        self._assert_data_is_correct_type(data=data)

        expected_result = [[20, 4, 1, 64], [20, 3, 216, 128]]
        assert data == expected_result

    def test_no_rx_port(self, parser: argparse.ArgumentParser) -> None:
        args = self.base_args + [
            '-M',
            '1',
        ]

        data = self._get_data_from_cli_args(parser=parser, args=args)
        self._assert_data_is_correct_type(data=data)

        # Shouldn't this test fail?
        # I think we need to refactor to use os.system...
        expected_result = [[20, 4, 1, 64], [20, 3, 1, 128]]
        assert data == expected_result
