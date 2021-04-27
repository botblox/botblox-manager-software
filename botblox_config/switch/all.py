from .switch import SwitchChip
from .switchblox import Switchblox
from .switchblox_nano import SwitchbloxNano


def create_switch(switch_type: str) -> SwitchChip:
    """
    Return an instance of a switch based on its name.
    :param switch_type: Name of the switch.
    :return: The switch instance.
    """
    if switch_type == "switchblox":
        return Switchblox()
    elif switch_type == "switchblox_nano" or switch_type == "nano":
        return SwitchbloxNano()
    else:
        raise ValueError("Unknown switch type '{}'".format(switch_type))
