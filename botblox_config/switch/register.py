from enum import Enum
from typing import Generic, List, TypeVar

from . import fields
from .utils import get_bit, set_bit


class RegisterAddress:
    """AddressType of a register."""

    def __eq__(self, other: 'RegisterAddress') -> bool:
        """
        Check if this address points to the same memory as other.
        :param other: The other address to compare.
        :return: Whether the addresses point to the same memory.
        """
        raise NotImplementedError()

    def __hash__(self) -> int:
        raise NotImplementedError()


class MIIRegisterAddress(RegisterAddress):
    """
    MIIM protocol register address.
    """

    def __init__(self, phy: int, mii: int) -> None:
        """
        :param phy: PHY address.
        :param mii: MII address.
        """
        self.phy = phy
        self.mii = mii

    def __eq__(self, other: 'MIIRegisterAddress') -> bool:
        return self.phy == other.phy and self.mii == other.mii

    def __hash__(self) -> int:
        return hash((self.phy, self.mii))


class ByteOrder(Enum):
    """
    Byte order of stored bytes.
    """
    LITTLE_ENDIAN = "little"
    BIG_ENDIAN = "big"


AddressType = TypeVar('AddressType')


class Register(Generic[AddressType]):
    """
    A configuration register on the switch.
    """

    def __init__(self, address: AddressType, num_data_bytes: int, byte_order: ByteOrder = ByteOrder.LITTLE_ENDIAN) \
            -> None:
        """
        :param address: Register address.
        :param num_data_bytes: Byte size of the data the register holds.
        :param byte_order: Order of bytes in the register.
        """
        self.address = address
        self.num_data_bytes = num_data_bytes
        self.byte_order = byte_order
        self.data: bytearray = bytearray(num_data_bytes)  # lowest byte first
        self._fields = list()

    def check_byte_index(self, index: int) -> None:
        """
        Check that the given index is valid as offset for a byte field in the register.
        :param index: The index to check.
        :raise ValueError: If the index is invalid.
        """
        if index >= self.num_data_bytes or index < 0:
            raise ValueError("Wrong byte index {} for switch chip with {}-byte registers".format(
                index, self.num_data_bytes))

    def check_bit_index(self, index: int) -> None:
        """
        Check that the given index is valid as offset for a bit field in the register.
        :param index: The index to check.
        :raise ValueError: If the index is invalid.
        """
        if index >= 8 * self.num_data_bytes or index < 0:
            raise ValueError("Wrong bit index {} for switch chip with {}-byte registers".format(
                index, self.num_data_bytes))

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
        return int.from_bytes(self.data, byteorder=self.byte_order.value, signed=signed)

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
        self.data = bytearray(num.to_bytes(len(self.data), byteorder=self.byte_order.value, signed=False))

    def add_field(self, field: 'fields.ConfigField') -> None:
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


class MIIRegister(Register[MIIRegisterAddress]):
    """
    A memory register on the switch.
    """

    def __init__(self, phy: int, mii: int) -> None:
        """
        :param phy: PHY address.
        :param mii: MII address.
        """
        super(MIIRegister, self).__init__(MIIRegisterAddress(phy, mii), 2)
