"""Package for containing data manager functions to convert user input to commands."""

from .portmirror_config import portmirror_create_configuration
from .vlan_config import vlan_create_configuration

__all__ = [
    'portmirror_create_configuration',
    'vlan_create_configuration',
]
