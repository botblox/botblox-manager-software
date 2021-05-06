from argparse import Action, Namespace
from typing import (AnyStr, List, Tuple)

from .switch_config import SwitchConfigCLI


class EraseConfigCLI(SwitchConfigCLI):
    """
    The "erase" action that removes all stored items from the EEPROM memory.
    """
    def __init__(self, subparsers: Action, switch_name: AnyStr) -> None:
        super().__init__(subparsers, switch_name)

        self._subparser = self._subparsers.add_parser(
            "erase",
            help="Erase all configuration",
        )
        self._subparser.set_defaults(execute=self.apply)

    def apply(self, args: Namespace) -> SwitchConfigCLI:
        return self

    def create_configuration(self) -> List[List[int]]:
        return [[101, 0, 0, 0]]
