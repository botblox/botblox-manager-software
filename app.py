"""Module adding CLI subparsers together."""

import datetime
import logging

import serial
from serial.tools import list_ports

logging.basicConfig(level=logging.DEBUG)


def test_pyserial(
    #device_name: str,
) -> None:
    """Test serial commands can be sent given device."""
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        timeout=1000,
        write_timeout=1000,
    )
    data = 45
    logging.debug(list_ports.comports()[0])
    ser.write(bytes(chr(data), encoding='utf8'))
    ser.close()


test_pyserial()