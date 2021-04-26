from botblox_config.switch.switch import Register, SwitchChip, PortListField


class ChipStub(SwitchChip):
    def name(self) -> str:
        return "stub"

    def _init_features(self):
        pass

    def _init_ports(self):
        pass

    def _init_registers(self):
        pass

    def _init_fields(self):
        pass

    def _create_port_list_field(self, register: Register, index: int, ports_default: bool,
                                name: str) -> PortListField:
        pass


class TestRegister:
    def test_register_zero(self):
        r = Register(1, 2, ChipStub())
        assert r.phy == 1
        assert r.mii == 2
        assert len(r.as_bytes()) == 2
        assert r.as_bytes()[0] == 0
        assert r.as_bytes()[1] == 0
        assert r.get_byte(0) == 0
        assert r.get_byte(1) == 0
        assert r.get_bit(0) == 0
        assert r.get_bit(1) == 0
        assert r.get_bit(8) == 0
        assert r.get_bit(15) == 0

        try:
            r.get_bit(16)
            assert False
        except ValueError:
            pass

        assert r.as_number() == 0
        assert r.as_number(signed=True) == 0
        assert r.is_default()

        for i in range(16):
            r.check_bit_index(i)
        try:
            r.check_bit_index(16)
            assert False
        except ValueError:
            pass

        r.check_byte_index(0)
        r.check_byte_index(1)
        try:
            r.check_byte_index(2)
            assert False
        except ValueError:
            pass

    def test_register_set_bit_in_first_byte(self):
        r = Register(3, 4, ChipStub())
        r.set_bit(0, True)
        assert r.phy == 3
        assert r.mii == 4
        assert len(r.as_bytes()) == 2
        assert r.as_bytes()[0] == 1
        assert r.as_bytes()[1] == 0
        assert r.get_byte(0) == 1
        assert r.get_byte(1) == 0
        assert r.get_bit(0) == 1
        assert r.get_bit(1) == 0
        assert r.get_bit(8) == 0
        assert r.get_bit(15) == 0

        assert r.as_number() == 1
        assert r.as_number(signed=True) == 1
        assert r.is_default()

    def test_register_set_bit_in_second_byte(self):
        r = Register(3, 4, ChipStub())
        r.set_bit(10, True)
        assert r.as_bytes()[0] == 0
        assert r.as_bytes()[1] == 0b0000_0100
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]
        assert r.get_bit(0) == 0
        assert r.get_bit(1) == 0
        assert r.get_bit(9) == 0
        assert r.get_bit(10) == 1
        assert r.get_bit(11) == 0
        assert r.get_bit(15) == 0

        assert r.as_number() == 0b0000_0100_0000_0000
        assert r.as_number(signed=True) == 0b0000_0100_0000_0000

    def test_register_set_two_bits(self):
        r = Register(3, 4, ChipStub())
        r.set_bit(2, True)
        r.set_bit(10, True)
        assert r.as_bytes()[0] == 0b0000_0100
        assert r.as_bytes()[1] == 0b0000_0100
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]
        assert r.get_bit(0) == 0
        assert r.get_bit(1) == 0
        assert r.get_bit(2) == 1
        assert r.get_bit(3) == 0
        assert r.get_bit(9) == 0
        assert r.get_bit(10) == 1
        assert r.get_bit(11) == 0
        assert r.get_bit(15) == 0

        assert r.as_number() == 0b0000_0100_0000_0100
        assert r.as_number(signed=True) == 0b0000_0100_0000_0100

    def test_register_reset_bit(self):
        r = Register(3, 4, ChipStub())
        r.set_bit(2, True)
        r.set_bit(2, False)
        assert r.as_bytes()[0] == 0
        assert r.as_bytes()[1] == 0
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]
        assert r.get_bit(0) == 0
        assert r.get_bit(1) == 0
        assert r.get_bit(2) == 0
        assert r.get_bit(3) == 0
        assert r.get_bit(15) == 0

        assert r.as_number() == 0
        assert r.as_number(signed=True) == 0

    def test_register_set_bit_as_signed(self):
        r = Register(3, 4, ChipStub())
        r.set_bit(15, True)
        assert r.as_number() == pow(2, 15)
        assert r.as_number(signed=True) == -pow(2, 15)

    def test_register_set_first_byte(self):
        r = Register(3, 4, ChipStub())
        r.set_byte(0, 100)
        assert len(r.as_bytes()) == 2
        assert r.as_bytes()[0] == 100
        assert r.as_bytes()[1] == 0
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]

        assert r.as_number() == 100
        assert r.as_number(signed=True) == 100

    def test_register_set_second_byte(self):
        r = Register(3, 4, ChipStub())
        r.set_byte(1, 0xCC)
        assert len(r.as_bytes()) == 2
        assert r.as_bytes()[0] == 0
        assert r.as_bytes()[1] == 0xCC
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]

        assert r.as_number() == 0xCC00
        assert r.as_number(signed=True) == -13312

    def test_register_set_both_bytes(self):
        r = Register(3, 4, ChipStub())
        r.set_byte(0, 0xCC)
        r.set_byte(1, 0xDD)
        assert len(r.as_bytes()) == 2
        assert r.as_bytes()[0] == 0xCC
        assert r.as_bytes()[1] == 0xDD
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]

        assert r.as_number() == 0xDDCC

    def test_register_set_bits(self):
        r = Register(3, 4, ChipStub())
        r.set_bits(6, 4, 0b1010)
        assert r.as_bytes()[0] == 0b1000_0000
        assert r.as_bytes()[1] == 0b0000_0010
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]
        assert r.get_bit(0) == 0
        assert r.get_bit(6) == 0
        assert r.get_bit(7) == 1
        assert r.get_bit(8) == 0
        assert r.get_bit(9) == 1
        assert r.get_bit(15) == 0

        assert r.as_number() == 0b0000_0010_1000_0000

    def test_register_set_all_bits(self):
        r = Register(3, 4, ChipStub())
        r.set_bits(0, 16, 0b1010_0101_1100_1111)
        assert r.as_bytes()[0] == 0b1100_1111
        assert r.as_bytes()[1] == 0b1010_0101
        assert r.get_byte(0) == r.as_bytes()[0]
        assert r.get_byte(1) == r.as_bytes()[1]
        assert r.get_bit(0) == 1
        assert r.get_bit(1) == 1
        assert r.get_bit(2) == 1
        assert r.get_bit(3) == 1
        assert r.get_bit(4) == 0
        assert r.get_bit(5) == 0
        assert r.get_bit(6) == 1
        assert r.get_bit(7) == 1
        assert r.get_bit(8) == 1
        assert r.get_bit(9) == 0
        assert r.get_bit(10) == 1
        assert r.get_bit(11) == 0
        assert r.get_bit(12) == 0
        assert r.get_bit(13) == 1
        assert r.get_bit(14) == 0
        assert r.get_bit(15) == 1

        assert r.as_number() == 0b1010_0101_1100_1111
