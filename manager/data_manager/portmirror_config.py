"""Define helper functions to convert the user port mirror configuration to commands for the firmware."""

from typing import (
    List,
    Optional,
    Tuple,
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
    settings: Optional[Union[List[int], str, int]],
) -> None:
    """Create section of parser data command for port mirror option.

    For a given option for port mirror, link the user input on the command line with
    the given choices corresponding to that input from the `portmirror_miim_register_map`.
    Some choices for options allow multiple choices to be selected and so each choice must
    be bitwise 'OR'-ed with each other to create the parser data for that option.
    For 'enable', given that no user explicity specifies that as an arg, it is automatically
    assigned the apprioriate value for activated port mirroring.

    :param str option: individual port mirror option
    :param Optional[Union[List[int], str, int]] settings: Can be a string relating to the port mirror mode (i.e. 'RX'),
        int relating to mirror_port (i.e. 1) or
        List[int] of multiple choices for other options (i.e. [1, 2] for `tx_port`)
    :rtype: None
    """
    if option == 'enable':
        portmirror_miim_register_map[option]['data'] = 1
        return

    choice_mapping = portmirror_miim_register_map[option]['choice_mapping']
    if type(settings) == list:
        individual_setting_data = [choice_mapping[setting] for setting in settings]
    else:
        individual_setting_data = [choice_mapping[settings]]

    data = 0
    if len(individual_setting_data) > 1:
        for setting_data in individual_setting_data:
            data = data | setting_data
    else:
        data = individual_setting_data[0]

    portmirror_miim_register_map[option]['data'] = data


def is_command_already_present(
    data: List[List],
    option: str,
) -> Tuple[bool, Union[int, None]]:
    """Calculate if a command writing to same PHY and REG already exists in data.

    Loops over current commands in data and determines if a command with the same PHY and REG is present.
    If so, return a tuple with (True, <index_of_command_in_data>).
    Else, return a tuple with (False, None)

    :param List[Union[List, None]] data: Current commands created, nullable input.
    :param str option: individual port mirror option
    :return: object with boolean flag and index representing position in list where command already exists
        for same PHY and REG
    :rtype: Tuple[bool, Union[int, None]]

    :example:

    >>> data=[[20, 3, 0, 128]]
    >>> option='mode'
    >>> is_command_already_present(data, option)
    (True, 0)
    """
    if data:
        for index_in_data, command in enumerate(data):
            is_command_with_same_phy = portmirror_miim_register_map[option]['phy'] == command[0]
            is_command_with_same_reg = portmirror_miim_register_map[option]['reg'] == command[1]
            if is_command_with_same_phy and is_command_with_same_reg:
                return (True, index_in_data)

    return (False, None)


def update_command(
    command_to_update: List,
    option: str,
) -> List:
    """Update a command when it is found that two parts of data share the same PHY and REG.

    Use the `portmirror_miim_register_map` to update the command with the register offset of the
    new data that shared the same PHY and REG. If two user inputs refer to data
    that share the same PHY and REG, then it needs to be part of the same command.

    :param List command_to_update: Current command that needs to be updated with new data.
    :param str option: individual port mirror option
    :return: Updated command with data regarding the current port
    :rtype: List
    """
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
    """Create a new command with PHY and REG plus two bytes of command data.

    Use the `portmirror_miim_register_map` to create the command.
    If reset is defined in user command line arguments, then we reset the
    port mirror to be system defaults. Elsewise use data in the
    `portmirror_miim_register_map`.

    :param str option: individual port mirror option
    :return: New created command
    :rtype: List
    """
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
    """Update data commands for setting the port mirror configuration.

    If this function is executed before the `portmirror_miim_register_map` is filled out,
    this will return system defaults for port mirroing

    :param List[List] data: current list of commands
    :param int port: physical port
    :return: Command for physical port
    :rtype: List[List]
    """
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

    >>> args=Namespace(execute=<function portmirror_create_configuration at {pointer}>,
                       mirror_port=[4], mode='RXandTX', rx_port=[1, 2], tx_port=[3, 5])
    >>> portmirror_create_configuration(args)
    [[20, 3, 12, 192], [20, 4, 144, 192]]

    >>> args=Namespace(execute=<function portmirror_create_configuration at {pointer}>,
                       mirror_port=5, mode='RX', reset=True)
    >>> portmirror_create_configuration(args)
    [[20, 3, 1, 0], [20, 4, 1, 224]]
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
