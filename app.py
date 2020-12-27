"""File for defining BotBlox CLI."""

import argparse
import logging
import sys
import time
from typing import (
    List,
    Optional,
)

import serial

from vlan_config import vlan_create_configuration

logging.basicConfig(level=logging.DEBUG)


def write_data_to_serial(
    data: List[List],
    device_name: Optional[str] = '/dev/ttyUSB0',
) -> bool:
    """Write data commands to serial port.

    Write data to serial port which the UART converter is connected to. The STM32 MCU
    on the SwitchBlox will then be interrupted and carry out the commands

    :param List[List] data: Commands created to write to STM32 MCU
    :param Optional[str] device_name: serial port device name (default: '/dev/ttyUSB0')
    :return: Flag to indicate whether the write data to serial was successful or not
    :rtype: bool
    """
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
    except IndexError:
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
    """Define all cli parser and subparsers here."""
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

    vlan_parser_group = vlan_parser.add_mutually_exclusive_group()
    vlan_parser_group.add_argument(
        '-g',
        '--group',
        nargs='+',
        action='append',
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=False,
        help='''Define the VLAN member groups using port number,
        i.e. --group 1 2 --group 3 4 puts makes Group A have
        ports 1 and 2, and Group B have ports 3 and 4'''
    )
    vlan_parser_group.add_argument(
        '-r',
        '--reset',
        action='store_true',
        default=argparse.SUPPRESS,
        help='''Reset the VLAN configuration to be as system default'''
    )
    vlan_parser_group.set_defaults(execute=vlan_create_configuration)

    if len(sys.argv) <= 1:
        sys.argv.append('--help')

    args = parser.parse_args()
    data = args.execute(args)

    # add stop command
    data.append([100, 0, 0, 0])

    is_success = write_data_to_serial(data)

    if is_success:
        logging.info('Successful configuration')
    else:
        logging.error('Failed to configure - check logs')


if __name__ == '__main__':
    main_cli()
