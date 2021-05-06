from enum import Enum
from typing import AnyStr, Dict, Iterable, List, Optional, Set


def get_bit(num: int, index: int) -> bool:
    """
    Get the index-th bit of num.
    """
    mask = 1 << index
    return bool(num & mask)


def set_bit(num: int, index: int, value: bool) -> int:
    """
    Set the index-th bit of num to 1 if value is truthy, else to 0, and return the new value.
    From https://stackoverflow.com/a/12174051/1076564 .
    """
    mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
    num &= ~mask          # Clear the bit indicated by the mask (if x is False)
    if value:
        num |= mask         # If x was True, set the bit indicated by the mask.
    return num            # Return the result, we're done.


class Port:
    def __init__(self, name: str, port_id: int) -> None:
        """
        :param name: Name of the port. This name is used in CLI commands to refer to the port.
        :param port_id: ID of the port. For internal use by the library.
        """
        self.name = name
        self.id = port_id

    def __repr__(self) -> str:
        return self.name


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


class SwitchChip:
    """
    Representation of a switch chip and its configuration fields and registers.
    """
    def __init__(self) -> None:
        self._features: Set[SwitchFeature] = set()
        self._ports: List[Port] = list()
        self._registers: Dict[int, Dict[int, Register]] = dict()
        self.fields: Dict[str, MIIField] = dict()

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

    def num_mii_bytes(self) -> int:
        """
        :return: Size of registers in bytes.
        """
        return 2

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

    def register_to_command(self, register: 'Register', leave_out_default: bool = True) -> Optional[List[int]]:
        """
        Convert the given register into a "command" for botblox firmware.
        :param register: The register to convert.
        :param leave_out_default: If true, returns None in case the register has its default value.
        :return: The firmware "command".
        """
        if leave_out_default and register.is_default():
            return None
        return [register.phy, register.mii] + register.as_bytes()

    def registers_to_commands(self, leave_out_default: bool = True, only_touched: bool = False) -> List[List[int]]:
        """
        Convert all registers into "commands" for botblox firmware.
        :param leave_out_default: If true, returns only the registers with value different from their default.
        :param only_touched: If true, returns only registers that were touched.
        :return: List of firmware "commands".
        """
        result = list()
        for phy in self._registers:
            for r in self._registers[phy].values():
                cmd = self.register_to_command(r, leave_out_default)
                if cmd is not None and (not only_touched or r.is_touched()):
                    result.append(cmd)
        result.sort()
        return result

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

    def get_registers(self) -> Dict[int, Dict[int, 'Register']]:
        """
        :return: All registers of the switch.
        """
        return self._registers

    def _add_register(self, register: 'Register') -> None:
        """
        Add the given register to this switch. This method should only be called during initialization.
        :param register: The register to add.
        """
        if register.phy not in self._registers:
            self._registers[register.phy] = dict()
        self._registers[register.phy][register.mii] = register

    def _add_field(self, field: 'MIIField') -> None:
        """
        Add the given field to this switch. This method should only be called during initialization.
        :param field: The field to add.
        """
        self.fields[field.get_name()] = field

    def _create_port_list_field(self, register: 'Register', index: int, ports_default: bool, name: str)\
            -> 'PortListField':
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


class Register:
    """
    A memory register on the switch.
    """

    def __init__(self, phy: int, mii: int, chip: SwitchChip) -> None:
        """
        :param phy: PHY address.
        :param mii: MII address.
        :param chip: The chip the register belongs to.
        """
        self.phy = phy
        self.mii = mii
        self.chip = chip
        self.data: bytearray = bytearray(chip.num_mii_bytes())  # lowest byte first
        self._fields = list()

    def check_byte_index(self, index: int) -> None:
        """
        Check that the given index is valid as offset for a byte field in the register.
        :param index: The index to check.
        :raise ValueError: If the index is invalid.
        """
        if index >= self.chip.num_mii_bytes() or index < 0:
            raise ValueError("Wrong byte index {} for switch chip with {}-byte registers".format(
                index, self.chip.num_mii_bytes()))

    def check_bit_index(self, index: int) -> None:
        """
        Check that the given index is valid as offset for a bit field in the register.
        :param index: The index to check.
        :raise ValueError: If the index is invalid.
        """
        if index >= 8 * self.chip.num_mii_bytes() or index < 0:
            raise ValueError("Wrong bit index {} for switch chip with {}-byte registers".format(
                index, self.chip.num_mii_bytes()))

    def check_bits_spec(self, offset: int, length: int) -> None:
        """
        Check that the given offset and length specify a valid subset of indexes in the register.
        :param offset: The offset of the bits field.
        :param length: Length of the bits field.
        :raise ValueError: If the offset/length pair is invalid.
        """
        self.check_bit_index(offset)
        self.check_bit_index(offset + length - 1)

    def as_bytes(self) -> List[int]:
        """
        :return: The byte values of the register.
        """
        return list(self.data)

    def as_number(self, signed: bool = False) -> int:
        """
        :param signed: Whether it should be treated as a signed integer.
        :return: Interpret the register as a single little-endian integer.
        """
        return int.from_bytes(self.data, byteorder='little', signed=signed)

    def get_byte(self, index: int) -> int:
        """
        Get the value of the byte at the given index.
        :param index: Index of the byte.
        :return: Value of the byte.
        """
        self.check_byte_index(index)
        return self.data[index]

    def set_byte(self, index: int, value: int) -> None:
        """
        Set value of the byte at the given index.
        :param index: Index of the byte.
        :param value: New value.
        """
        self.check_byte_index(index)
        if value > 255:
            raise ValueError("Invalid byte value " + str(value))
        self.data[index] = value

    def get_bit(self, index: int) -> bool:
        """
        Get the value of the bit at the given index.
        :param index: Index of the bit.
        :return: Value of the bit.
        """
        self.check_bit_index(index)
        byte_index = index // 8
        bit_offset = index % 8
        return get_bit(self.data[byte_index], bit_offset)

    def set_bit(self, index: int, value: bool) -> None:
        """
        Set value of the bit at the given index.
        :param index: Index of the bit.
        :param value: New value.
        """
        self.check_bit_index(index)
        byte_index = index // 8
        bit_offset = index % 8
        self.data[byte_index] = set_bit(self.data[byte_index], bit_offset, value)

    def get_bits(self, offset: int, length: int) -> int:
        """
        Get the value of the bits at the given offset.
        :param offset: Starting offset of the bits (counted from LSB).
        :param length: Number of bits.
        :return: Value of the bits.
        """
        self.check_bits_spec(offset, length)
        num = self.as_number()
        mask = (pow(2, length) - 1) << offset
        return (num & mask) >> offset

    def set_bits(self, offset: int, length: int, value: int) -> None:
        """
        Set the value of the bits at the given offset.
        :param offset: Starting offset of the bits (counted from LSB).
        :param length: Number of bits.
        :param value: The value to set.
        :raise ValueError: If value is too big to fit into length bits.
        """
        self.check_bits_spec(offset, length)
        if value >= pow(2, length):
            raise ValueError("Value {} doesn't fit into a {}-bit field".format(value, length))
        num = self.as_number(signed=False)
        mask = (pow(2, length) - 1) << offset
        num &= ~mask  # zero out bits
        num += (value << offset)
        self.data = bytearray(num.to_bytes(len(self.data), byteorder='little', signed=False))

    def add_field(self, field: 'MIIField') -> None:
        """
        Attach the given field to this register.
        :param field: The field to add.
        """
        self._fields.append(field)

    def is_default(self) -> bool:
        """
        :return: Whether the register has its default value.
        """
        for field in self._fields:
            if not field.is_default():
                return False
        return True

    def is_touched(self) -> bool:
        """
        :return: Whether any bit in this register has been touched.
        """
        for field in self._fields:
            if field.is_touched():
                return True
        return False


class MIIField:
    """
    Configuration field of a switch.
    """
    def __init__(self, register: Register, name: str) -> None:
        """
        :param register: The register on which this field works.
        :param name: Name of the field.
        """
        self._register = register
        self._name = name
        self._touched = False
        register.add_field(self)

    def get_name(self) -> str:
        """
        :return: Name of the field.
        """
        return self._name

    def is_default(self) -> bool:
        """
        :return: Whether the field has its default value.
        """
        raise NotImplementedError()

    def set_default(self, touch: bool = True) -> None:
        """
        Set the field to its default value.
        :param touch: Whether to set the touched flag.
        """
        raise NotImplementedError()

    def is_touched(self) -> bool:
        """
        :return: Whether the field has been touched.
        """
        return self._touched

    def __str__(self) -> str:
        return self.get_name()


class DataField(MIIField):
    """
    A general data-holding field.
    """
    def __init__(self, register: Register, default: int, name: str) -> None:
        """
        :param register: The register on which this field works.
        :param default: Default value of the field.
        :param name: Name of the field.
        """
        super().__init__(register, name)
        self._default = default

    def get_value(self) -> int:
        """
        :return: The value of the field.
        """
        raise NotImplementedError()

    def set_value(self, value: int, touch: bool = True) -> None:
        """
        Set value of the field.
        :param value: The value to set.
        :param touch: Whether to set the touched flag.
        """
        raise NotImplementedError()

    def is_default(self) -> bool:
        return self.get_value() == self._default

    def set_default(self, touch: bool = True) -> None:
        self.set_value(self._default, touch)

    def __str__(self) -> str:
        return self.get_name() + "={}".format(self.get_value())


class BitField(DataField):
    """
    A field holding a single bit.
    """
    def __init__(self, register: Register, index: int, default: bool, name: str) -> None:
        super().__init__(register, default, name)
        self._index = index
        self.set_value(default, touch=False)

    def get_value(self) -> bool:
        return self._register.get_bit(self._index)

    def set_value(self, value: bool, touch: bool = True) -> None:
        self._register.set_bit(self._index, value)
        if touch:
            self._touched = True

    def __str__(self) -> str:
        return self.get_name() + "=1b'" + ("1" if self.get_value() else "0")


class BitsField(DataField):
    """
    A field holding a sequence of bits.
    """
    def __init__(self, register: Register, offset: int, length: int, default: int, name: str) -> None:
        super().__init__(register, default, name)
        self._offset = offset
        self._length = length
        self.set_value(default, touch=False)

    def get_value(self) -> int:
        return self._register.get_bits(self._offset, self._length)

    def set_value(self, value: int, touch: bool = True) -> None:
        self._register.set_bits(self._offset, self._length, value)
        if touch:
            self._touched = True

    def get_bit(self, index: int) -> bool:
        return get_bit(self.get_value(), index)

    def set_bit(self, index: int, value: bool) -> None:
        self.set_value(set_bit(self.get_value(), index, value))

    def __str__(self) -> str:
        return self.get_name() + ("={0}b'{1:0" + str(self._length) + "b}({1})").format(self._length, self.get_value())


class ByteField(DataField):
    """
    A field holding one byte.
    """
    def __init__(self, register: Register, index: int, default: int, name: str) -> None:
        super().__init__(register, default, name)
        self._index = index
        self.set_value(default, touch=False)

    def get_value(self) -> int:
        return self._register.get_byte(self._index)

    def set_value(self, value: int, touch: bool = True) -> None:
        self._register.set_byte(self._index, value)
        if touch:
            self._touched = True

    def __str__(self) -> str:
        return self.get_name() + "=8h'{0:02X}({0})".format(self.get_value())


class ShortField(DataField):
    """
    A field holding one 16-bit number.
    """
    def __init__(self, register: Register, byte_offset: int, default: int, name: str) -> None:
        super().__init__(register, default, name)
        self._byte_offset = byte_offset
        self.set_value(default, touch=False)

    def get_value(self) -> int:
        return self._register.get_byte(self._byte_offset) + (self._register.get_byte(self._byte_offset + 1) * 256)

    def set_value(self, value: int, touch: bool = True) -> None:
        self._register.set_byte(self._byte_offset, value % 256)
        self._register.set_byte(self._byte_offset + 1, value // 256)
        if touch:
            self._touched = True

    def __str__(self) -> str:
        return self.get_name() + "=16h'{0:04X}({0})".format(self.get_value())


class PortListField(MIIField):
    """
    A field holding a set/list of ports.
    """
    def __init__(self, register: Register, all_ports: List[Port], ports_default: bool, name: str) -> None:
        """
        :param register: The register on which this field works.
        :param all_ports: List of all available ports.
        :param ports_default: Whether to set all ports by default.
        :param name: Name of the field.
        """
        super().__init__(register, name)
        self._ports_default: bool = ports_default
        self._ports: Dict[int, Port] = dict()
        self._all_ports: List[Port] = all_ports
        if ports_default:
            self._ports = dict([(p.id, p) for p in self._all_ports])

    def add_port(self, port: Port, touch: bool = True) -> None:
        """
        Add the given port to the list.
        :param port: The port to add.
        :param touch: Whether to set the touched flag.
        """
        self._touched |= touch
        if port.id in self._ports:
            return
        self._ports[port.id] = port
        self._add_port(port, touch)

    def _add_port(self, port: Port, touch: bool = True) -> None:
        """
        Switch-specific implementation.
        """
        raise NotImplementedError()

    def remove_port(self, port: Port, touch: bool = True) -> None:
        """
        Remove the given port from the list.
        :param port: The port to remove.
        :param touch: Whether to set the touched flag.
        """
        self._touched |= touch
        if port.id not in self._ports:
            return
        del self._ports[port.id]
        self._remove_port(port)

    def _remove_port(self, port: Port, touch: bool = True) -> None:
        """
        Switch-specific implementation.
        """
        raise NotImplementedError()

    def set_port(self, port: Port, value: bool, touch: bool = True) -> None:
        """
        Set the given port in this list (True adds it, False removes it).
        :param port: The port to handle.
        :param value: Whether to add or remove the port.
        :param touch: Whether to set the touched flag.
        """
        if value:
            self.add_port(port, touch)
        else:
            self.remove_port(port, touch)

    def clear(self, touch: bool = True) -> None:
        """
        Remove all ports from the list.
        :param touch: Whether to set the touched flag.
        """
        self._touched |= touch
        self._ports.clear()
        self._clear(touch)

    def _clear(self, touch: bool = True) -> None:
        """
        Switch-specific implementation.
        """
        raise NotImplementedError()

    def is_port_set(self, port: Port) -> bool:
        """
        Return whether the given port is a member of this list.
        :param port: The port to search.
        :return: Whether the given port is a member of this list.
        """
        return port.id in self._ports

    def get_ports(self) -> List[Port]:
        """
        :return: All ports that are set in this field.
        """
        return list(self._ports.values())

    def is_default(self) -> bool:
        """
        :return: Whether this field has its default value.
        """
        return (len(self._ports) > 0) == self._ports_default

    def set_default(self, touch: bool = True) -> None:
        """
        Set this field to its default value.
        :param touch: Whether to set the touched flag.
        """
        self._touched |= touch
        if self._ports_default:
            self._ports = dict([(p.id, p) for p in self._all_ports])
            for p in self._all_ports:
                self._add_port(p, touch)
        else:
            self._ports = dict()
            for p in self._all_ports:
                self._remove_port(p, touch)

    def __str__(self) -> str:
        return self.get_name() + "=Ports[{}]".format(",".join([p.name for p in self._ports.values()]))
