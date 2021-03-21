from argparse import ArgumentParser
from typing import (Any, List)


class TestSetReset:
    package: List[str] = ['botblox']
    base_args: List[str] = [
        '--device',
        'usb_usart_converter_device',
        'vlan',
        '--reset',
    ]

    @staticmethod
    def _assert_data_is_correct_type(
        *,
        data: Any,
    ) -> None:
        assert len(data) > 0
        assert len(data[0]) == 4
        assert isinstance(data, list)
        assert isinstance(data[0], list)
        assert isinstance(data[0][0], int)

    @staticmethod
    def _get_data_from_cli_args(
        *,
        parser: ArgumentParser,
        args: List[str],
    ) -> List[List[int]]:
        parsed_args = parser.parse_args(args)
        config = parsed_args.execute(parsed_args)
        return config.create_configuration()

    def test_reset(
        self,
        parser: ArgumentParser,
    ) -> None:
        data = self._get_data_from_cli_args(
            parser=parser,
            args=self.base_args,
        )
        self._assert_data_is_correct_type(data=data)

        expected_result = [[23, 16, 255, 255], [23, 17, 255, 0], [23, 18, 255, 255]]
        assert data == expected_result
