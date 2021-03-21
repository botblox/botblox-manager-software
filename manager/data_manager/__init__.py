"""Package for containing data manager functions to convert user input to commands."""

from manager.data_manager.mirror import PortMirrorConfig
from manager.data_manager.vlan import VlanConfig

__all__ = [
    PortMirrorConfig,
    VlanConfig,
]
