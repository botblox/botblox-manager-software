from manager.switch.switch import set_bit, get_bit


class TestBitOps:
    def test_get_bit(self):
        num = 0b001
        assert get_bit(num, 0) == True
        assert get_bit(num, 1) == False
        assert get_bit(num, 2) == False
        assert get_bit(num, 3) == False

        num = 0b101010
        assert get_bit(num, 0) == False
        assert get_bit(num, 1) == True
        assert get_bit(num, 2) == False
        assert get_bit(num, 3) == True
        assert get_bit(num, 4) == False
        assert get_bit(num, 5) == True

        num = 0
        for i in range(30):
            assert get_bit(num, i) == False

        num = 256 - 1
        for i in range(8):
            assert get_bit(num, i) == True

    def test_set_bit(self):
        num = 0
        assert set_bit(num, 0, True) == 0b1
        assert set_bit(num, 3, True) == 0b1000
        assert set_bit(num, 12, True) == 0b1000000000000

        num = 256 - 1
        assert set_bit(num, 0, False) == 0b11111110
        assert set_bit(num, 3, False) == 0b11110111
        assert set_bit(num, 7, False) == 0b01111111

        num = 0
        num = set_bit(num, 0, True)
        num = set_bit(num, 3, True)
        assert num == 0b1001
        num = set_bit(num, 2, True)
        assert num == 0b1101
        num = set_bit(num, 1, False)
        assert num == 0b1101
        num = set_bit(num, 2, False)
        assert num == 0b1001
        num = set_bit(num, 0, False)
        assert num == 0b1000
        num = set_bit(num, 3, False)
        assert num == 0b0000
