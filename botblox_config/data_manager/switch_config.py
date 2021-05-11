from argparse import Action, Namespace
from typing import List

from ..switch import Port, SwitchChip


class SwitchConfig:
    """
    A particular semantic configuration of a switch chip.
    """
    def __init__(self, switch: SwitchChip) -> None:
        """
        :param switch: The switch to which this configuration belongs.
        """
        self._switch = switch

    def apply_to_switch(self) -> None:
        """
        Apply this configuration to the switch object (set the appropriate fields and registers).
        """
        raise NotImplementedError()

    def _num_ports(self) -> int:
        return self._switch.num_ports()

    def _ports(self) -> List[Port]:
        return self._switch.ports()

    def _get_port(self, index: int) -> Port:
        if not 0 <= index < self._num_ports():
            raise ValueError("Port number {} does not exist in switch chip {}", index, self._switch.name())
        return self._ports()[index]


class SwitchConfigCLI:
    """
    Command-Line Interface for the semantic switch configuration.
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        self._subparsers = subparsers
        self._switch = switch

    def apply(self, args: Namespace) -> 'SwitchConfigCLI':
        """
        Load the given CLI args.
        :param args: CLI args.
        :return: Self.
        """
        raise NotImplementedError()

    # TODO (anyone): when all commands are converted to use the switch class, this method can be left out and
    #                switch.get_commands() can be called directly from the CLI class.
    def create_configuration(self) -> List[List[int]]:
        """
        :return: A SwitchConfig parsed from the CLI args passed previously to apply().
        """
        raise NotImplementedError()
