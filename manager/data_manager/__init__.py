"""Package for containing data manager functions to convert user input to commands."""

from .mirror_config import PortMirrorConfig
from .portmirror_config import PortMirror  # DEPRECATED
from .vlan_config import vlan_create_configuration


__all__ = [
    'PortMirror',
    'PortMirrorConfig',
    'vlan_create_configuration',
]
