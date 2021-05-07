from enum import Enum
from typing import AnyStr, Dict, Generic, Iterable, List, Optional, Set, Type, TypeVar

from .config_writer import ConfigWriter, TestWriter
from .fields import ConfigField
from .port import Port
from .register import Register, RegisterAddress


class SwitchFeature(Enum):
    TAGGED_VLAN = "tagged VLAN configuration"
    VLAN_TABLE = "VLAN table"
    VLAN_MODE_OPTIONAL = "VLAN mode Optional"
    VLAN_MODE_ENABLE = "VLAN mode Enable"
    VLAN_MODE_STRICT = "VLAN mode Strict"
    VLAN_FORCE = "VLAN ID forcing"
    PER_PORT_VLAN_MODE = "per-port VLAN mode"
    PER_PORT_VLAN_MODE_DISABLE = "per-port VLAN mode Disable"
    PER_PORT_VLAN_MODE_OPTIONAL = "per-port VLAN mode Optional"
    PER_PORT_VLAN_MODE_ENABLE = "per-port VLAN mode Enable"
    PER_PORT_VLAN_MODE_STRICT = "per-port VLAN mode Strict"
    PER_PORT_VLAN_RECEIVE_MODE = "per-port VLAN receive mode"
    PER_PORT_VLAN_FORCE = "per-port force VLAN ID"
    PER_PORT_VLAN_HEADER_ACTION = "per-port VLAN header action"
    PER_VLAN_HEADER_ACTION = "VLAN header action per port and VLAN"


RegisterAddressType = TypeVar('RegisterAddressType', bound=RegisterAddress)
RegisterType = TypeVar('RegisterType', bound=Register)
CommandType = TypeVar('CommandType')


class SwitchChip(Generic[RegisterAddressType, RegisterType, CommandType]):
    """
    Representation of a switch chip and its configuration fields and registers.
    """
    def __init__(self) -> None:
        self._features: Set[SwitchFeature] = set()
        self._ports: List[Port] = list()
        self._registers: Dict[RegisterAddressType, RegisterType] = dict()
        self.fields: Dict[str, ConfigField] = dict()

        self._init_features()
        self._init_ports()
        self._init_registers()
        self._init_fields()

        for field in self.fields.values():
            field.set_default(touch=False)

    def name(self) -> str:
        """
        Return a user-friendly name of the chip.
        """
        raise NotImplementedError()

    def max_vlans(self) -> int:
        """
        :return: Maximum number of allowed VLANs in VLAN table. Zero if VLANs are not supported.
        """
        return 16

    def max_vlan_id(self) -> int:
        """
        :return: Maximum supported VLAN ID. Zero if VLANs are not supported.
        """
        return 4096

    def num_ports(self) -> int:
        """
        :return: Number of ports this switch has.
        """
        return len(self._ports)

    def ports(self) -> List[Port]:
        """
        :return: The ports this switch has.
        """
        return self._ports

    def get_port(self, name: AnyStr) -> Port:
        """
        Get port by name.
        :param name: The name to search for.
        :return: Port with the given name.
        :raise ValueError: If the port doesn't exist.
        """
        for port in self._ports:
            if port.name == name:
                return port
        raise ValueError("Invalid port '{}'".format(name))

    def port_names(self) -> Iterable[AnyStr]:
        """
        :return: Names of all ports.
        """
        return map(lambda p: p.name, self._ports)

    def get_commands(self, leave_out_default: bool = True, only_touched: bool = False) -> CommandType:
        """
        Convert all registers into "commands" for botblox firmware.
        :param leave_out_default: If true, returns only the registers with value different from their default.
        :param only_touched: If true, returns only registers that were touched.
        :return: Firmware "commands".
        """
        raise NotImplementedError()

    def get_config_writer_description(self) -> str:
        """
        :return: Human-readable short description of the device that writes configuration to the device. E.g. "UART to
                 USB converter"
        """
        return self._get_config_writer_type().device_description()

    def _get_config_writer_type(self) -> Type[ConfigWriter]:
        """
        :return: Type of the config writer.
        """
        raise NotImplementedError()

    def get_config_writer(self, device_name: str) -> ConfigWriter:
        """
        Return an instance of config writer for this switch.
        :param device_name: Name of the config writer device to use.
        :return: The config writer.
        :raises ValueError: If the passed device is not valid.
        """
        if device_name == "test":
            return TestWriter(device_name)
        return self._get_config_writer_type()(device_name)

    def _init_features(self) -> None:
        """
        Initialize self._features .
        """
        raise NotImplementedError()

    def _init_ports(self) -> None:
        """
        Initialize self._ports.
        """
        raise NotImplementedError()

    def _init_registers(self) -> None:
        """
        Initialize self._registers.
        """
        raise NotImplementedError()

    def _init_fields(self) -> None:
        """
        Initialize self._fields.
        """
        raise NotImplementedError()

    def get_registers(self) -> Dict[RegisterAddressType, RegisterType]:
        """
        :return: All registers of the switch.
        """
        return self._registers

    def _add_register(self, register: RegisterType) -> None:
        """
        Add the given register to this switch. This method should only be called during initialization.
        :param register: The register to add.
        """
        self._registers[register.address] = register

    def _add_field(self, field: ConfigField) -> None:
        """
        Add the given field to this switch. This method should only be called during initialization.
        :param field: The field to add.
        """
        self.fields[field.get_name()] = field

    def _create_port_list_field(self, register: RegisterType, index: int, ports_default: bool, name: str) \
            -> ConfigField:
        """
        Create a field that represents a bitmask (or other representation) of a set/list of ports.
        :param register: The register that backs this list.
        :param index: Index in the register (implementation-specific).
        :param ports_default: Whether all ports should be set by default or not.
        :param name: Name of the field.
        :return: The field.
        """
        raise NotImplementedError()

    def parse_vlan_id(self, vlan_str: AnyStr) -> int:
        """
        Parse VLAN ID from string.
        :param vlan_str: The string to parse.
        :return: Numeric representation of the VLAN ID.
        :raises ValueError: If the value is not convertible to int or if it is out of the valid VLAN ID range.
        """
        num = int(vlan_str)  # ValueError can be thrown, but that's expected for non-int inputs
        if (num < 0) or (num > self.max_vlan_id()):
            raise ValueError("{} is not valid VLAN ID (max is {})".format(vlan_str, self.max_vlan_id()))
        return num

    def check_vlan_id(self, vlan_id: int) -> None:
        """
        Check whether the given VLAN ID is valid.
        :param vlan_id: The ID to check.
        :raise ValueError: If it's invalid.
        """
        if not 0 <= vlan_id < self.max_vlan_id():
            raise ValueError("VLAN ID {} is invalid for {} with max VLAN ID {}".format(
                             vlan_id, self.name(), self.max_vlan_id()))

    def has_feature(self, feature: SwitchFeature) -> bool:
        """
        Check if this switch has the given feature.
        :param feature: The feature to check.
        :return: Whether the switch has the feature.
        """
        return feature in self._features

    def check_feature(self, feature: SwitchFeature) -> None:
        """
        Check that this switch has the given feature.
        :param feature: The feature to check.
        :raise RuntimeError: If the switch does not have the feature.
        """
        if not self.has_feature(feature):
            raise RuntimeError("{} does not support {}".format(self.name(), feature.value))
        pass
