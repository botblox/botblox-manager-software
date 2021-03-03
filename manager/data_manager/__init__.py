"""Package for containing data manager functions to convert user input to commands."""

from manager.data_manager.mirror_config import PortMirrorConfig
from manager.data_manager.portmirror_config import PortMirror  # DEPRECATED
from manager.data_manager.vlan_config import vlan_create_configuration


__all__ = [
    'PortMirror',
    'PortMirrorConfig',
    'vlan_create_configuration',
]
