from typing import Dict, List

from . import register
from .port import Port
from .utils import get_bit, set_bit


class ConfigField:
    """
    Configuration field of a switch.
    """
    def __init__(self, register: 'register.Register', name: str) -> None:
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


class DirectValueField(ConfigField):
    """
    A general data-holding field.
    """
    def __init__(self, register: 'register.Register', default: int, name: str) -> None:
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


class BitField(DirectValueField):
    """
    A field holding a single bit.
    """
    def __init__(self, register: 'register.Register', index: int, default: bool, name: str) -> None:
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


class BitsField(DirectValueField):
    """
    A field holding a sequence of bits.
    """
    def __init__(self, register: 'register.Register', offset: int, length: int, default: int, name: str) -> None:
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


class ByteField(DirectValueField):
    """
    A field holding one byte.
    """
    def __init__(self, register: 'register.Register', index: int, default: int, name: str) -> None:
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


class ShortField(DirectValueField):
    """
    A field holding one 16-bit number.
    """
    def __init__(self, register: 'register.Register', byte_offset: int, default: int, name: str) -> None:
        if register.num_data_bytes <= 1:
            raise RuntimeError("Register {} cannot hold 16-bit values.".format(register))
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


class PortListField(ConfigField):
    """
    A field holding a set/list of ports.
    """
    def __init__(self, register: 'register.Register', all_ports: List[Port], ports_default: bool, name: str) -> None:
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
