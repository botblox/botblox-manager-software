"""File for defining BotBlox CLI."""

import argparse
import time
import logging
import sys
from typing import (
    List,
    Optional,
)

import serial
from serial.tools import list_ports

from vlan_config import vlan_create_configuration

logging.basicConfig(level=logging.DEBUG)

def write_data_to_serial(
    data: List[List],
    device_name: Optional[str] = '/dev/ttyUSB0',
) -> bool:
    ser = serial.Serial(
        port=device_name,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        timeout=20,
        write_timeout=2,
    )

    for command in data:
        x = bytes(command)
        ser.write(x)
        time.sleep(0.1)

    condition = ser.read(size=1)
    ser.close()

    try:
        condition = list(condition)[0]
    except IndexError as index_err:
        logging.error('Failed to read condition message from board')
        return False
    else:
        if condition == 1:
            logging.info('Success setting configuration in EEPROM')
            return True
        elif condition == 2:
            logging.error('Failed saving configuration in EEPROM')
            return False
    

def main_cli() -> None:
    """Define all cli parser and subparsers here"""
    parser = argparse.ArgumentParser(
        description='CLI for configuring SwitchBlox managed settings',
        epilog='Please open an issue on https://github.com/botblox/botblox-manager-software/ if there is a problem',
    )
    subparsers = parser.add_subparsers(
        title='Individual group commands for each configuration',
        description='Please choose a certain command',
        required=True,
    )

    vlan_parser = subparsers.add_parser(
        'vlan',
        help='Configure the ports to be in VLAN groups',
    )
    vlan_parser.add_argument(
        '-g',
        '--group',
        nargs='+',
        action='append',
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=True,
    )
    vlan_parser.set_defaults(execute=vlan_create_configuration)

    if len(sys.argv) <= 1:
        sys.argv.append('--help')

    args = parser.parse_args()
    data = args.execute(args.group)

    # add stop command
    data.append([100, 0, 0, 0])

    is_success = write_data_to_serial(data)

    if is_success:
        logging.info('Successful configuration')
    else:
        logging.error('Failed to configure - check logs')


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


# test_pyserial()


if __name__ == '__main__':
    main_cli()
