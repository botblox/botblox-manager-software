"""File for defining BotBlox CLI."""

import argparse
import logging
import sys
import time
from typing import List

import serial

from .data_manager import (
    PortMirrorConfig,
    VlanConfig,
    TagVlanConfigCLI,
    EraseConfigCLI
)

logging.basicConfig(level=logging.DEBUG)


def write_data_to_serial(
    data: List[List],
    device_name: str,
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


def create_parser(argv=None) -> argparse.ArgumentParser:
    """Define all cli parser and subparsers here."""
    parser = argparse.ArgumentParser(
        description='CLI for configuring SwitchBlox managed settings',
        epilog='Please open any issue on https://github.com/botblox/botblox-manager-software/ if there is a problem',
    )
    parser.add_argument(
        '-D',
        '--device',
        type=str,
        help='Select the USB-to-UART converter device. Set to "test" to disable actual writing to the serial line.',
        nargs='?',
        required=True,
    )
    parser.add_argument(
        '-S',
        '--switch',
        type=str,
        choices=("switchblox", "switchblox_nano", "nano"),
        help='Select the type of the connected switch (default is switchblox)',
        nargs='?',
        default="switchblox",
        required=False,
    )

    try:
        if argv is None:
            argv = sys.argv
        switch_namespace, _ = parser.parse_known_args(list(filter(lambda a: a != '-h' and a != '--help', argv)))
        switch_name = switch_namespace.switch
    except argparse.ArgumentError as e:
        switch_name = "switchblox"
        print(str(e))

    subparsers = parser.add_subparsers(
        title='Individual group commands for each configuration',
        description='Please choose a certain command',
        required=True,
    )

    # VLAN CLI
    vlan_parser = subparsers.add_parser(
        'vlan',
        help='Configure the ports to be in VLAN groups',
    )
    vlan_parser_group = vlan_parser.add_mutually_exclusive_group(required=True)
    vlan_parser_group.add_argument(
        '-g',
        '--group',
        nargs='+',
        action='append',
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=False,
        help='''Define the VLAN member groups using port number,
        i.e. --group 1 2 --group 3 4 makes Group A have
        ports 1 and 2 and Group B have ports 3 and 4. All unmentioned
        ports are assigned to default group. If a group has only 1 port,
        the port gets isolated. In this example, port 5 would
        not be allowed to communicate with any other port.'''
    )
    vlan_parser_group.add_argument(
        '-r',
        '--reset',
        action='store_true',
        default=argparse.SUPPRESS,
        help='''Reset the VLAN configuration to be as system default'''
    )
    vlan_parser_group.set_defaults(execute=VlanConfig)

    # Port mirroring CLI
    portmirror_parser = subparsers.add_parser(
        'mirror',
        help='Configure the ports to mirror traffic',
    )
    portmirror_parser_mutex_grouping = portmirror_parser.add_mutually_exclusive_group()
    portmirror_parser_config_group = portmirror_parser_mutex_grouping.add_argument_group()

    portmirror_parser_config_group.add_argument(
        '-m',
        '--mode',
        nargs='?',
        default='RX',
        type=str,
        choices=['RX', 'TX', 'RXorTX', 'RXandTX'],
        required=False,
        help='''Select the mirror mode during operation''',
    )
    portmirror_parser_config_group.add_argument(
        '-M',
        '--mirror-port',
        nargs=1,
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=False,
        default=5,
        help='''Select the mirror port (default: port 5)''',
    )
    portmirror_parser_config_group.add_argument(
        '-rx',
        '--rx-port',
        nargs='+',
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=any(mode in sys.argv for mode in ['RX', 'RXorTX', 'RXandTX']),
        default=argparse.SUPPRESS,
        help='''Select the source (receive) port to be mirrored''',
    )
    portmirror_parser_config_group.add_argument(
        '-tx',
        '--tx-port',
        nargs='+',
        type=int,
        choices=[1, 2, 3, 4, 5],
        required=any(mode in sys.argv for mode in ['TX', 'RXorTX', 'RXandTX']),
        default=argparse.SUPPRESS,
        help='''Select the destination (transmit) port to be mirrored''',
    )
    portmirror_parser_mutex_grouping.add_argument(
        '-r',
        '--reset',
        action='store_true',
        default=argparse.SUPPRESS,
        help='Reset the Port mirroring configuration to default, this will turn port mirroring off'
    )
    # (1) DEPRECATED
    # portmirror_parser_mutex_grouping.set_defaults(execute=PortMirror().create_configuration)
    # (2)
    portmirror_parser_mutex_grouping.set_defaults(execute=PortMirrorConfig)

    commands = list()
    commands.append(TagVlanConfigCLI(subparsers, switch_name))
    commands.append(EraseConfigCLI(subparsers, switch_name))

    return parser


def cli() -> None:
    parser = create_parser()

    if len(sys.argv) <= 1:
        sys.argv.append('--help')

    args = parser.parse_args()

    config = args.execute(args)
    data: List[List[int]] = config.create_configuration()

    logging.debug('Data to be sent (excl. "stop" command): ')
    logging.debug('------------------------------------------')
    logging.debug(data)
    logging.debug('------------------------------------------')

    # add stop command
    data.append([100, 0, 0, 0])

    logging.debug('Data sent (inc. "stop" command): ')
    logging.debug('------------------------------------------')
    logging.debug(data)
    logging.debug('------------------------------------------')

    device_name = args.device
    if device_name != "test":
        is_success = write_data_to_serial(data=data, device_name=device_name)

        if is_success:
            logging.info('Successful configuration')
        else:
            logging.error('Failed to configure - check logs')
    else:
        logging.info('Test device used, no data were written to any serial port')
