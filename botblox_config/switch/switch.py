from enum import Enum
from typing import Set, List, Dict, Union, AnyStr, Iterable


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
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id

    def __repr__(self):
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
    def __init__(self):
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
        raise NotImplementedError()

    def num_mii_bytes(self) -> int:
        return 2

    def max_vlans(self) -> int:
        return 16

    def max_vlan_id(self) -> int:
        return 4096

    def num_ports(self) -> int:
        return len(self._ports)

    def ports(self) -> List[Port]:
        return self._ports

    def get_port(self, name: AnyStr) -> Port:
        for port in self._ports:
            if port.name == name:
                return port
        raise ValueError("Invalid port '{}'".format(name))

    def port_names(self) -> Iterable[AnyStr]:
        return map(lambda p: p.name, self._ports)

    def register_to_command(self, register: 'Register', leave_out_default: bool = True) -> Union[List[int], None]:
        if leave_out_default and register.is_default():
            return None
        return [register.phy, register.mii] + register.as_bytes()

    def registers_to_commands(self, leave_out_default: bool = True, only_touched: bool = False) -> List[List[int]]:
        result = list()
        for phy in self._registers:
            for r in self._registers[phy].values():
                cmd = self.register_to_command(r, leave_out_default)
                if cmd is not None and (not only_touched or r.is_touched()):
                    result.append(cmd)
        result.sort()
        return result

    def _init_features(self):
        raise NotImplementedError()

    def _init_ports(self):
        raise NotImplementedError()

    def _init_registers(self):
        raise NotImplementedError()

    def _init_fields(self):
        raise NotImplementedError()

    def get_registers(self):
        return self._registers

    def _add_register(self, register: 'Register'):
        if register.phy not in self._registers:
            self._registers[register.phy] = dict()
        self._registers[register.phy][register.mii] = register

    def _add_field(self, field: 'MIIField'):
        self.fields[field.get_name()] = field

    def _create_port_list_field(self, register: 'Register', index: int, ports_default: bool, name: str) -> 'PortListField':
        raise NotImplementedError()

    def check_vlan_id(self, vlan_id):
        if not 0 <= vlan_id < self.max_vlan_id():
            raise ValueError("VLAN ID {} is invalid for {} with max VLAN ID {}".format(
                             vlan_id, self.name(), self.max_vlan_id()))

    def has_feature(self, feature: SwitchFeature):
        return feature in self._features

    def check_feature(self, feature: SwitchFeature):
        if not self.has_feature(feature):
            raise RuntimeError("{} does not support {}".format(self.name(), feature.value))
        pass


class Register:
    def __init__(self, phy: int, mii: int, chip: SwitchChip):
        self.phy = phy
        self.mii = mii
        self.chip = chip
        self.data: bytearray = bytearray(chip.num_mii_bytes())  # lowest byte first
        self._fields = list()

    def check_byte_index(self, index: int):
        if index >= self.chip.num_mii_bytes() or index < 0:
            raise ValueError("Wrong byte index {} for switch chip with {}-byte registers".format(index, self.chip.num_mii_bytes()))

    def check_bit_index(self, index: int):
        if index >= 8 * self.chip.num_mii_bytes() or index < 0:
            raise ValueError("Wrong bit index {} for switch chip with {}-byte registers".format(index, self.chip.num_mii_bytes()))

    def check_bits_spec(self, offset: int, length: int):
        self.check_bit_index(offset)
        self.check_bit_index(offset + length - 1)

    def as_bytes(self) -> List[int]:
        return list(self.data)

    def as_number(self, signed: bool = False) -> int:
        return int.from_bytes(self.data, byteorder='little', signed=signed)

    def get_byte(self, index: int) -> int:
        self.check_byte_index(index)
        return self.data[index]

    def set_byte(self, index: int, value: int):
        self.check_byte_index(index)
        if value > 255:
            raise ValueError("Invalid byte value " + str(value))
        self.data[index] = value

    def get_bit(self, index: int) -> bool:
        self.check_bit_index(index)
        byte_index = index // 8
        bit_offset = index % 8
        return get_bit(self.data[byte_index], bit_offset)

    def set_bit(self, index: int, value: bool):
        self.check_bit_index(index)
        byte_index = index // 8
        bit_offset = index % 8
        self.data[byte_index] = set_bit(self.data[byte_index], bit_offset, value)

    def get_bits(self, offset: int, length: int) -> int:
        self.check_bits_spec(offset, length)
        num = self.as_number()
        mask = (pow(2, length) - 1) << offset
        return (num & mask) >> offset

    def set_bits(self, offset: int, length: int, value: int):
        self.check_bits_spec(offset, length)
        if value >= pow(2, length):
            raise ValueError("Value {} doesn't fit into a {}-bit field".format(value, length))
        num = self.as_number(signed=False)
        mask = (pow(2, length) - 1) << offset
        num &= ~mask  # zero out bits
        num += (value << offset)
        self.data = bytearray(num.to_bytes(len(self.data), byteorder='little', signed=False))

    def add_field(self, field: 'MIIField'):
        self._fields.append(field)

    def is_default(self) -> bool:
        for field in self._fields:
            if not field.is_default():
                return False
        return True

    def is_touched(self) -> bool:
        for field in self._fields:
            if field.is_touched():
                return True
        return False


class MIIField:
    def __init__(self, register: Register, name: str):
        self._register = register
        self._name = name
        self._touched = False
        register.add_field(self)

    def get_name(self) -> str:
        return self._name

    def is_default(self) -> bool:
        raise NotImplementedError()

    def set_default(self, touch=True):
        raise NotImplementedError()

    def is_touched(self) -> bool:
        return self._touched

    def __str__(self) -> str:
        return self.get_name()


class DataField(MIIField):
    def __init__(self, register: Register, default: int, name: str):
        super().__init__(register, name)
        self._default = default

    def get_value(self) -> int:
        raise NotImplementedError()

    def set_value(self, value: int, touch=True):
        raise NotImplementedError()

    def is_default(self) -> bool:
        return self.get_value() == self._default

    def set_default(self, touch=True):
        self.set_value(self._default, touch)

    def __str__(self) -> str:
        return self.get_name() + "={}".format(self.get_value())


class BitField(DataField):
    def __init__(self, register: Register, index: int, default: bool, name: str):
        super().__init__(register, default, name)
        self._index = index
        self.set_value(default, touch=False)

    def get_value(self) -> bool:
        return self._register.get_bit(self._index)

    def set_value(self, value: bool, touch=True):
        self._register.set_bit(self._index, value)
        if touch:
            self._touched = True

    def __str__(self) -> str:
        return self.get_name() + "=1b'" + ("1" if self.get_value() else "0")


class BitsField(DataField):
    def __init__(self, register: Register, offset: int, length: int, default: int, name: str):
        super().__init__(register, default, name)
        self._offset = offset
        self._length = length
        self.set_value(default, touch=False)

    def get_value(self) -> int:
        return self._register.get_bits(self._offset, self._length)

    def set_value(self, value: int, touch=True):
        self._register.set_bits(self._offset, self._length, value)
        if touch:
            self._touched = True

    def get_bit(self, index: int) -> bool:
        return get_bit(self.get_value(), index)

    def set_bit(self, index: int, value: bool):
        self.set_value(set_bit(self.get_value(), index, value))

    def __str__(self) -> str:
        return self.get_name() + ("={0}b'{1:0" + str(self._length) + "b}({1})").format(self._length, self.get_value())


class ByteField(DataField):
    def __init__(self, register: Register, index: int, default: int, name: str):
        super().__init__(register, default, name)
        self._index = index
        self.set_value(default, touch=False)

    def get_value(self) -> int:
        return self._register.get_byte(self._index)

    def set_value(self, value: int, touch=True):
        self._register.set_byte(self._index, value)
        if touch:
            self._touched = True

    def __str__(self) -> str:
        return self.get_name() + "=8h'{0:02X}({0})".format(self.get_value())


class ShortField(DataField):
    def __init__(self, register: Register, byte_offset: int, default: int, name: str):
        super().__init__(register, default, name)
        self._byte_offset = byte_offset
        self.set_value(default, touch=False)

    def get_value(self) -> int:
        return self._register.get_byte(self._byte_offset) + (self._register.get_byte(self._byte_offset + 1) * 256)

    def set_value(self, value: int, touch=True):
        self._register.set_byte(self._byte_offset, value % 256)
        self._register.set_byte(self._byte_offset + 1, value // 256)
        if touch:
            self._touched = True

    def __str__(self) -> str:
        return self.get_name() + "=16h'{0:04X}({0})".format(self.get_value())


class PortListField(MIIField):
    def __init__(self, register: Register, all_ports: List[Port], ports_default: bool, name: str):
        super().__init__(register, name)
        self._ports_default: bool = ports_default
        self._ports: Dict[int, Port] = dict()
        self._all_ports: List[Port] = all_ports
        if ports_default:
            self._ports = dict([(p.id, p) for p in self._all_ports])

    def add_port(self, port: Port, touch: bool = True):
        self._touched |= touch
        if port.id in self._ports:
            return
        self._ports[port.id] = port
        self._add_port(port, touch)

    def _add_port(self, port: Port, touch: bool = True):
        raise NotImplementedError()

    def remove_port(self, port: Port, touch: bool = True):
        self._touched |= touch
        if port.id not in self._ports:
            return
        del self._ports[port.id]
        self._remove_port(port)

    def _remove_port(self, port: Port, touch: bool = True):
        raise NotImplementedError()

    def set_port(self, port: Port, value: bool, touch: bool = True):
        if value:
            self.add_port(port, touch)
        else:
            self.remove_port(port, touch)

    def clear(self, touch: bool = True):
        self._touched |= touch
        self._ports.clear()
        self._clear(touch)

    def _clear(self, touch: bool = True):
        raise NotImplementedError()

    def is_port_set(self, port: Port) -> bool:
        return port.id in self._ports

    def get_ports(self) -> List[Port]:
        return list(self._ports.values())

    def is_default(self) -> bool:
        return (len(self._ports) > 0) == self._ports_default

    def set_default(self, touch: bool = True):
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
