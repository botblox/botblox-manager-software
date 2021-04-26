from typing import List

from manager.switch.switch import Register, SwitchChip, BitField, BitsField, ByteField, ShortField, PortListField, \
    Port


class StubPortListField(PortListField):
    def __init__(self, register: Register, index: int, ports: List[Port], ports_default: bool, name: str):
        super().__init__(register, ports, ports_default, name)

    def _add_port(self, port: Port, touch: bool = True):
        pass

    def _remove_port(self, port: Port, touch: bool = True):
        pass

    def _clear(self, touch: bool = True):
        pass


class ChipStub(SwitchChip):
    def name(self) -> str:
        return "stub"

    def _init_features(self):
        pass

    def _init_ports(self):
        self._ports.append(Port("0", 0))
        self._ports.append(Port("1", 1))
        self._ports.append(Port("2", 3))

    def _init_registers(self):
        pass

    def _init_fields(self):
        pass

    def _create_port_list_field(self, register: Register, index: int, ports_default: bool, name: str) -> PortListField:
        return StubPortListField(register, index, self._ports, ports_default, name)


class TestField:
    def test_bit_field(self):
        r = Register(1, 2, ChipStub())
        f = BitField(r, 0, False, "test")

        assert f.get_name() == "test"
        assert f.get_value() == False
        assert f.is_default()
        assert r.as_number() == 0

        f.set_value(True)
        assert f.get_value() == True
        assert not f.is_default()
        assert r.as_number() == 1

        f.set_default()
        assert f.get_value() == False
        assert f.is_default()
        assert r.as_number() == 0

        f2 = BitField(r, 10, True, "test2")

        assert f2.get_name() == "test2"
        assert f2.get_value() == True
        assert f2.is_default()
        assert r.as_number() == 0b0000_0100_0000_0000

        f2.set_value(False)
        assert f2.get_value() == False
        assert not f2.is_default()
        assert r.as_number() == 0

        f2.set_default()
        assert f2.get_value() == True
        assert f2.is_default()
        assert r.as_number() == 0b0000_0100_0000_0000

        f.set_value(True)
        assert r.as_number() == 0b0000_0100_0000_0001

    def test_bits_field(self):
        r = Register(1, 2, ChipStub())
        f = BitsField(r, 6, 4, 0b0000, "test")

        assert f.get_name() == "test"
        assert f.get_value() == 0b0000
        assert f.is_default()
        assert r.as_number() == 0

        f.set_value(0b1010)
        assert f.get_value() == 0b1010
        assert not f.is_default()
        assert r.as_number() == 0b0000_0010_1000_0000

        f.set_default()
        assert f.get_value() == 0b0000
        assert f.is_default()
        assert r.as_number() == 0

        f2 = BitsField(r, 2, 3, 0b111, "test2")

        assert f2.get_name() == "test2"
        assert f2.get_value() == 0b111
        assert f2.is_default()
        assert r.as_number() == 0b0000_0000_0001_1100

        f2.set_value(0b010)
        assert f2.get_value() == 0b010
        assert not f2.is_default()
        assert r.as_number() == 0b0000_0000_0000_1000

        f2.set_default()
        assert f2.get_value() == 0b111
        assert f2.is_default()
        assert r.as_number() == 0b0000_0000_0001_1100

        f.set_value(0b1111)
        assert r.as_number() == 0b0000_0011_1101_1100

        f.set_bit(0, False)
        assert f.get_value() == 0b1110
        assert r.as_number() == 0b0000_0011_1001_1100

        f.set_bit(3, False)
        assert f.get_value() == 0b0110
        assert r.as_number() == 0b0000_0001_1001_1100

    def test_byte_field(self):
        r = Register(1, 2, ChipStub())
        f = ByteField(r, 0, 0, "test")

        assert f.get_name() == "test"
        assert f.get_value() == 0
        assert f.is_default()
        assert r.as_number() == 0

        f.set_value(0xCC)
        assert f.get_value() == 0xCC
        assert not f.is_default()
        assert r.as_number() == 0xCC

        f.set_default()
        assert f.get_value() == 0
        assert f.is_default()
        assert r.as_number() == 0

        f2 = ByteField(r, 1, 0xDD, "test2")

        assert f2.get_name() == "test2"
        assert f2.get_value() == 0xDD
        assert f2.is_default()
        assert r.as_number() == 0xDD00

        f2.set_value(0xEE)
        assert f2.get_value() == 0xEE
        assert not f2.is_default()
        assert r.as_number() == 0xEE00

        f2.set_default()
        assert f2.get_value() == 0xDD
        assert f2.is_default()
        assert r.as_number() == 0xDD00

        f.set_value(0xCC)
        assert r.as_number() == 0xDDCC

    def test_short_field(self):
        r = Register(1, 2, ChipStub())
        f = ShortField(r, 0, 0, "test")

        assert f.get_name() == "test"
        assert f.get_value() == 0
        assert f.is_default()
        assert r.as_number() == 0

        f.set_value(0xCCDD)
        assert f.get_value() == 0xCCDD
        assert not f.is_default()
        assert r.as_number() == 0xCCDD

        f.set_default()
        assert f.get_value() == 0
        assert f.is_default()
        assert r.as_number() == 0

    def test_port_list_field(self):
        switch = ChipStub()
        assert len(switch.ports()) == 3

        r = Register(1, 2, switch)
        f = switch._create_port_list_field(r, 0, False, "test")

        assert f.get_name() == "test"
        assert len(f.get_ports()) == 0
        for port in switch.ports():
            assert not f.is_port_set(port)

        f.add_port(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[0])
        assert f.is_port_set(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[2])

        f.set_port(switch.ports()[1], True)
        assert not f.is_port_set(switch.ports()[0])
        assert f.is_port_set(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[2])

        f.set_port(switch.ports()[1], False)
        assert not f.is_port_set(switch.ports()[0])
        assert not f.is_port_set(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[2])

        f.add_port(switch.ports()[1])
        f.remove_port(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[0])
        assert not f.is_port_set(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[2])

        f.add_port(switch.ports()[1])
        f.set_default()
        assert not f.is_port_set(switch.ports()[0])
        assert not f.is_port_set(switch.ports()[1])
        assert not f.is_port_set(switch.ports()[2])

        f2 = switch._create_port_list_field(r, 0, True, "test2")

        assert f2.get_name() == "test2"
        assert len(f2.get_ports()) == 3
        for port in switch.ports():
            assert f2.is_port_set(port)
