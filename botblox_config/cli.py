"""File for defining BotBlox CLI."""

import argparse
import logging
import sys
from typing import List, Tuple

from .data_manager import (
    EraseConfigCLI,
    PortMirrorConfig,
    TagVlanConfigCLI,
    VlanConfig,
)
from .switch import create_switch, SwitchChip

logging.basicConfig(level=logging.DEBUG)


def create_parser(argv: List[str] = None) -> Tuple[argparse.ArgumentParser, SwitchChip]:
    """Define all cli parser and subparsers here."""
    parser = argparse.ArgumentParser(
        description='CLI for configuring SwitchBlox managed settings',
        epilog='Please open any issue on https://github.com/botblox/botblox-manager-software/ if there is a problem',
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
        logging.error(str(e))

    switch = create_switch(switch_name)

    parser.add_argument(
        '-D',
        '--device',
        type=switch.get_config_writer,
        help='Select the {} device. Set to "test" to disable actual writing to the device.'.format(
            switch.get_config_writer_description()
        ),
        nargs='?',
        required=True,
    )

    subparsers = parser.add_subparsers(
        title='Individual group commands for each configuration',
        description='Please choose a certain command',
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
    commands.append(TagVlanConfigCLI(subparsers, switch))
    commands.append(EraseConfigCLI(subparsers, switch))

    return parser, switch


def cli() -> None:
    parser, switch = create_parser()

    if len(sys.argv) < 2:
        sys.argv.append('--help')
    elif len(sys.argv) == 3 and sys.argv[1] in ['--device', '-d']:
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
        writer = args.device
        is_success = writer.write(data)

        if is_success:
            logging.info('Successful configuration')
        else:
            logging.error('Failed to configure - check logs')
    else:
        logging.info('Test device used, no data were written to any serial port')
