"""Define helper functions to convert the user port mirror configuration to commands for the firmware."""

from typing import (
    Tuple,
    List,
    Optional,
    Union,
)

portmirror_miim_register_map = {
    'enable': {
        'name': 'PORT_MIRROR_EN',
        'phy': 20,
        'reg': 3,
        'size': 1,
        'offset': 15,
        'sys_default': 0,
        'data': -1,
    },
    'mode': {
        'name': 'PORT_MIRROR_MODE',
        'phy': 20, 
        'reg': 3,
        'size': 2,
        'offset': 13,
        'sys_default': 0,
        'data': -1,
        'choice_mapping': {
            'RX': 0b00,
            'TX': 0b01,
            'RXandTX': 0b10,
            'RXorTX': 0b11,
        },
    },
    'rx_port': {
        'name': 'SEL_RX_PORT_MIRROR',
        'phy': 20, 
        'reg': 3,
        'size': 8,
        'offset': 0,
        'sys_default': 0x01,
        'data': -1,
        'choice_mapping': {
            1: 0b00000100,
            2: 0b00001000,
            3: 0b00010000,
            4: 0b01000000,
            5: 0b10000000, 
        },
    },
    'mirror_port': {
        'name': 'SEL_MIRROR_PORT',
        'phy': 20,
        'reg': 4,
        'size': 3,
        'offset': 13,
        'sys_default': 0b111,
        'data': -1,
        'choice_mapping': {
            1: 0b010,
            2: 0b011,
            3: 0b100,
            4: 0b110,
            5: 0b111,
        },
    },
    'tx_port': {
        'name': 'SEL_TX_PORT_MIRROR',
        'phy': 20,
        'reg': 4,
        'size': 8,
        'offset': 0,
        'sys_default': 0x01,
        'data': -1,
        'choice_mapping': {
            1: 0b00000100,
            2: 0b00001000,
            3: 0b00010000,
            4: 0b01000000,
            5: 0b10000000, 
        },
    },
}


def create_portmirror_parser_data_per_option(
    option: str,
    settings: Optional[Union[List, str, int]],
) -> None:
    if option == 'enable':
        portmirror_miim_register_map[option]['data'] = 1
        return

    choice_mapping = portmirror_miim_register_map[option]['choice_mapping']
    if type(settings) == list:
        individual_setting_data = [choice_mapping[setting] for setting in settings]
    else:
        individual_setting_data = [choice_mapping[settings]]

    data = 0
    if type(individual_setting_data) == list and len(individual_setting_data) > 1:
        for setting_data in individual_setting_data:
            data = data | setting_data
    else:
        data = individual_setting_data[0]
    
    portmirror_miim_register_map[option]['data'] = data


def is_command_already_present(
    data: List[List],
    option: str,
) -> Tuple[bool, Union[int, None]]:
    if data:
        for index_in_data, command in enumerate(data):
            if portmirror_miim_register_map[option]['phy'] == command[0] and portmirror_miim_register_map[option]['reg'] == command[1]:
                return (True, index_in_data)

    return (False, None)


def update_command(
    command_to_update: List,
    option: str,
) -> List:
    if portmirror_miim_register_map[option]['data'] >= 0:
        option_data = portmirror_miim_register_map[option]['data']
    else:
        option_data = portmirror_miim_register_map[option]['sys_default']
    option_offset = portmirror_miim_register_map[option]['offset']

    command_to_update[2] = command_to_update[2] | ((option_data << option_offset) & 0xFF)
    command_to_update[3] = command_to_update[3] | (((option_data << option_offset) & 0xFF00) >> 8) 

    return command_to_update
  

def create_command(
    option: str,
    reset: Optional[bool] = False,
) -> List:
    if reset:
        option_data = portmirror_miim_register_map[option]['sys_default']
    else:
        option_data = portmirror_miim_register_map[option]['data']    
    option_offset = portmirror_miim_register_map[option]['offset']

    command = [
        portmirror_miim_register_map[option]['phy'],
        portmirror_miim_register_map[option]['reg'],
        (option_data << option_offset) & 0xFF,
        ((option_data << option_offset) & 0xFF00) >> 8,
    ]
    return command


def update_data(
    data: List[List],
    option: str,
    reset: Optional[bool] = False,
) -> List[List]:

    is_present, index_in_data = is_command_already_present(data, option)

    if is_present and index_in_data is not None:
        command_to_update = data[index_in_data]
        command_updated = update_command(command_to_update=command_to_update, option=option)
        data[index_in_data] = command_updated
    else:
        command = create_command(option=option, reset=reset)
        data.append(command)

    return data


def portmirror_create_configuration(
    args: Tuple,
) -> List[List]:
    """Create parser data from user input.

    :param Tuple args: command line arguments from user
    :return: list of commmands to be sent to the firmware
    :rtype: List[List]

    :example:
    """
    data = []
    mirror_options = list(portmirror_miim_register_map.keys())
    try: 
        args.reset
    except AttributeError:
        args_dict = vars(args)
    else:
        for mirror_option in mirror_options:
            data = update_data(data=data, option=mirror_option, reset=True)
        return data

    for mirror_option in mirror_options:
        if mirror_option == 'enable':
            create_portmirror_parser_data_per_option(option=mirror_option, settings=1)
        else:
            if args_dict.get(mirror_option, None) is not None:
                create_portmirror_parser_data_per_option(option=mirror_option, settings=args_dict[mirror_option])

        data = update_data(data=data, option=mirror_option)

    return data