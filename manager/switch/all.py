from .switchblox import Switchblox
from .switchblox_nano import SwitchbloxNano


def create_switch(switch_type: str):
    if switch_type == "switchblox":
        return Switchblox()
    elif switch_type == "switchblox_nano" or switch_type == "nano":
        return SwitchbloxNano()
    else:
        raise ValueError("Unknown switch type '{}'".format(switch_type))