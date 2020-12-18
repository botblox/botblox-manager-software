"""Module adding CLI subparsers together."""

import time
import logging

import serial
from serial.tools import list_ports

logging.basicConfig(level=logging.DEBUG)


def test_pyserial(
    # device_name: str,
) -> None:
    """Test serial commands can be sent given device."""
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        timeout=20,
        write_timeout=2,
    )
    # data = [[2, 0, 0, 0], [3, 0, 0, 0], [4, 0, 0, 48], [6, 0, 0, 48], [7, 0, 0, 0], [100, 0, 0, 0]]
    data = [[101, 0, 0, 0], [100, 0, 0, 0]]

    for command in data:
        x = bytes(command)
        ser.write(x)
        time.sleep(0.1)

    condition = ser.read(size=1)

    try:
        condition = list(condition)[0]
    except IndexError as index_err:
        logging.error('Failed to read condition message from board')
    else:
        if condition == 1:
            logging.info('Success setting configuration in EEPROM')
        elif condition == 2:
            logging.error('Failed saving configuration in EEPROM')

    ser.close()


test_pyserial()
