"""Define helper functions to convert the user vlan configuration to commands for the firmware."""

from typing import (
    List,
    Tuple,
    Union,
)

vlan_miim_register_map = {
    1: {
        'name': 'PBV_MEMBER_P0',
        'phy': 23,
        'reg': 16,
        'size': 8,
        'offset': 0,
        'sys_default': 0xFF,
        'data': 0,
    },
    2: {
        'name': 'PBV_MEMBER_P1',
        'phy': 23,
        'reg': 16,
        'size': 8,
        'offset': 8,
        'sys_default': 0xFF,
        'data': 0,
    },
    3: {
        'name': 'PBV_MEMBER_P2',
        'phy': 23,
        'reg': 17,
        'size': 8,
        'offset': 0,
        'sys_default': 0xFF,
        'data': 0,
    },
    4: {
        'name': 'PBV_MEMBER_P3',
        'phy': 23,
        'reg': 18,
        'size': 8,
        'offset': 0,
        'sys_default': 0xFF,
        'data': 0,
    },
    5: {
        'name': 'PBV_MEMBER_P4',
        'phy': 23,
        'reg': 18,
        'size': 8,
        'offset': 8,
        'sys_default': 0xFF,
        'data': 0,
    },
}

vlan_binary_offset_map = {
        1: 2,
        2: 3,
        3: 4,
        4: 6,
        5: 7,
}


def get_unique_ports(
    numbers: List,
) -> List:
    """Get unique member ports.

    Returns only the unique ports that a single port shares VLAN membership with

    :param List numbers: List of ports a single port shares VLAN membership, duplicates allowed.
    :return: List of ports a single port shares VLAN membership, duplicates forbidden.
    :rtype: List

    :example:

    >>> numbers=[1, 1, 2, 3, 4]
    >>> get_unique_ports(numbers)
    [1, 2, 3, 4]
    """
    unique = []
    for number in numbers:
        if number not in unique:
            unique.append(number)
    return unique


def create_vlan_parser_data_per_port(
    vlan_members: List,
    port: int,
) -> None:
    """Create section of parser data command per port.

    Loops over members ports for each physical port and create the data in the shape so that it can be used
    by the parser when further checks on duplicate commands are made.

    :param List vlan_members: List of the member ports belonging to the physical port
    :param int port: individual physical port
    :rtype: None
    """
    for other_port in vlan_members:
        vlan_miim_register_map[port]['data'] = vlan_miim_register_map[port]['data'] | (
            1 << vlan_binary_offset_map[other_port])


def is_command_already_present(
    data: List[Union[List, None]],
    port: int,
) -> Tuple[bool, Union[int, None]]:
    """Calculate if a command writing to same PHY and REG exists.

    Loops over current commands and determines if a command with the same PHY and REG is present.
    If so, return a tuple with (True, <index_of_command_in_data>).
    Else, return a tuple with (False, None)

    :param List[Union[List, None]] data: Current commands created, nullable input.
    :param int port: individual physical port
    :return: object with boolean flag and index representing position in list where command already exists
        for same PHY and REG
    :rtype: Tuple[bool, Union[int, None]]

    :example:

    >>> data=[[23, 16, 0, 0]]
    >>> port=2
    >>> is_command_already_present(data, port)
    (True, 0)
    """
    if data:
        for index_in_data, command in enumerate(data):
            if vlan_miim_register_map[port]['phy'] == command[0] and vlan_miim_register_map[port]['reg'] == command[1]:
                return (True, index_in_data)

    return (False, None)


def update_command(
    command_to_update: List,
    port: int,
) -> List:
    """Update a command when it is found that two parts of data share the same PHY and REG.

    Use the `vlan_miim_register_map` to update the command with the register offset of the
    new data that shared the same PHY and REG.

    :param List command_to_update: Current command that needs to be updated with new data.
    :param int port: individual physical port
    :return: Updated command with data regarding the current port
    :rtype: List
    """
    port_data = 0
    if vlan_miim_register_map[port]['data'] != 0:
        port_data = vlan_miim_register_map[port]['data']
    else:
        port_data = vlan_miim_register_map[port]['sys_default']
    port_offset = vlan_miim_register_map[port]['offset']

    command_to_update[2] = command_to_update[2] | ((port_data << port_offset) & 0xFF)
    command_to_update[3] = command_to_update[3] | (((port_data << port_offset) & 0xFF00) >> port_offset)

    return command_to_update


def create_command(
    port: int,
) -> List:
    """Create a new command with PHY and REG plus two bytes of command data.

    Use the `vlan_miim_register_map` to create the command

    :param int port: individual physical port
    :return: Newly created command
    :rtype: List
    """
    port_data = 0
    if vlan_miim_register_map[port]['data'] != 0:
        port_data = vlan_miim_register_map[port]['data']
    else:
        port_data = vlan_miim_register_map[port]['sys_default']
    port_offset = vlan_miim_register_map[port]['offset']

    command = [
        vlan_miim_register_map[port]['phy'],
        vlan_miim_register_map[port]['reg'],
        (port_data << port_offset) & 0xFF,
        ((port_data << port_offset) & 0xFF00) >> port_offset,
    ]
    return command


def update_data(
    data: List[List],
    port: int,
) -> List[List]:
    """Update data commands for setting the VLAN configuration.

    If this function is executed before the `vlan_miim_register_map` is filled out,
    this will return system defaults

    :param List[List] data: current list of commands
    :param int port: physical port
    :return: Command for physical port
    :rtype: List[List]
    """
    is_present, index_in_data = is_command_already_present(data, port)

    if is_present and index_in_data is not None:
        command_to_update = data[index_in_data]
        command_updated = update_command(command_to_update=command_to_update, port=port)
        data[index_in_data] = command_updated
    else:
        command = create_command(port)
        data.append(command)

    return data


def vlan_create_configuration(
    args: Tuple,
) -> List[List]:
    """Create parser data from user input.

    :param Tuple args: command line arguments from user
    :return: list of commmands to be sent to the firmware
    :rtype: List[List]

    :example:

    >>> args=(execute=<function>, group=[[1, 2], [3, 4]])
    >>> vlan_create_configuration(groupings)
    [[23, 16, 12, 12], [23, 17, 80, 0], [23, 18, 80, 0]]

    >>> args=(execute=<function>, reset=True)
    >>> vlan_create_configuraton(groupings)
    [[23, 16, 255, 255], [23, 17, 255, 0], [23, 18, 255, 255]]
    """
    data = []
    ports = list(vlan_binary_offset_map.keys())
    try:
        args.reset
    except AttributeError:
        groupings = args.group
    else:
        for port in ports:
            data = update_data(data=data, port=port)
        return data

    for port in ports:
        vlan_members = []
        for grouping in groupings:
            if port in grouping:
                vlan_members += grouping

        vlan_members = get_unique_ports(vlan_members)

        create_vlan_parser_data_per_port(vlan_members=vlan_members, port=port)

        data = update_data(data=data, port=port)

    return data
