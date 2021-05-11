from typing import Type

from .switch import SwitchChip
from .switchblox import Switchblox
from .switchblox_nano import SwitchbloxNano


def get_switch_class(switch_type: str) -> Type[SwitchChip]:
    """
    Return class of a switch based on its name.
    :param switch_type: Name of the switch.
    :return: The switch class.
    """
    if switch_type == "switchblox":
        return Switchblox
    elif switch_type == "switchblox_nano" or switch_type == "nano":
        return SwitchbloxNano
    else:
        raise ValueError("Unknown switch type '{}'".format(switch_type))


def create_switch(switch_type: str) -> SwitchChip:
    """
    Return an instance of a switch based on its name.
    :param switch_type: Name of the switch.
    :return: The switch instance.
    """
    return get_switch_class(switch_type)()
