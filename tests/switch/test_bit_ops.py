from botblox_config.switch.utils import get_bit, set_bit


class TestBitOps:
    def test_get_bit(self) -> None:
        num = 0b001
        assert get_bit(num, 0) == True  # noqa: E712
        assert get_bit(num, 1) == False  # noqa: E712
        assert get_bit(num, 2) == False  # noqa: E712
        assert get_bit(num, 3) == False  # noqa: E712

        num = 0b101010
        assert get_bit(num, 0) == False  # noqa: E712
        assert get_bit(num, 1) == True  # noqa: E712
        assert get_bit(num, 2) == False  # noqa: E712
        assert get_bit(num, 3) == True  # noqa: E712
        assert get_bit(num, 4) == False  # noqa: E712
        assert get_bit(num, 5) == True  # noqa: E712

        num = 0
        for i in range(30):
            assert get_bit(num, i) == False  # noqa: E712

        num = 256 - 1
        for i in range(8):
            assert get_bit(num, i) == True  # noqa: E712

    def test_set_bit(self) -> None:
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
