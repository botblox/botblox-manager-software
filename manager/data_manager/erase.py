from typing import (
    List,
    Tuple,
    AnyStr
)

from .switch_config import SwitchConfig, SwitchConfigCLI


class EraseConfigCLI(SwitchConfigCLI):
    def __init__(self, subparsers, switch_name: AnyStr):
        super().__init__(subparsers, switch_name)

        self._subparser = self._subparsers.add_parser(
            "erase",
            help="Erase all configuration",
        )
        self._subparser.set_defaults(execute=lambda args: self.apply(args))

    def apply(self, args: Tuple) -> SwitchConfigCLI:
        return self

    def create_configuration(self) -> List[List[int]]:
        return [[101, 0, 0, 0]]
