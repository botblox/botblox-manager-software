from typing import (
    Dict,
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
        'sys_default': 0,
        'data': 0,
    },
    2: {
        'name': 'PBV_MEMBER_P1',
        'phy': 23,
        'reg': 16,
        'size': 8,
        'offset': 8,
        'sys_default': 0,
        'data': 0,
    },
    3: {
        'name': 'PBV_MEMBER_P2',
        'phy': 23,
        'reg': 17,
        'size': 8,
        'offset': 0,
        'sys_default': 0,
        'data': 0,
    },
    4: {
        'name': 'PBV_MEMBER_P3',
        'phy': 23,
        'reg': 18,
        'size': 8,
        'offset': 0,
        'sys_default': 0,
        'data': 0,
    },
    5: {
        'name': 'PBV_MEMBER_P4',
        'phy': 23,
        'reg': 18,
        'size': 8,
        'offset': 8,
        'sys_default': 0,
        'data': 0,
    },
}


def get_unique_ports(
    numbers: List,
) -> List:
    unique = []
    for number in numbers:
        if number not in unique:
            unique.append(number)
    return unique


def get_member_ports_per_port(
    ports: List,
    groupings: List[List],
    vlan_members: Dict[int, List]
) -> Dict[int, List]:
    for port in ports:
        for grouping in groupings:
            if port in grouping:
                vlan_members[port] += grouping
            vlan_members[port] = get_unique_ports(vlan_members[port])
    return vlan_members


def is_command_already_present(
    data: List[Union[List, None]],
    port: int,
) -> Tuple[bool, Union[int, None]]:
    if data:
        for index_in_data, command in enumerate(data):
            if vlan_miim_register_map[port]['phy'] == command[0] and vlan_miim_register_map[port]['reg'] == command[1]:
                return (True, index_in_data)

    return (False, None)


def vlan_create_configuration(
    groupings: List,
) -> List[List]:
    vlan_binary_offset_map = {
        1: 2,
        2: 3,
        3: 4,
        4: 6,
        5: 7,
    }

    vlan_members = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
    }

    ports = list(vlan_members.keys())
    vlan_members = get_member_ports_per_port(ports=ports, groupings=groupings, vlan_members=vlan_members)

    for port in ports:
        for other_port in vlan_members[port]:
            vlan_miim_register_map[port]['data'] = vlan_miim_register_map[port]['data'] | (
                1 << vlan_binary_offset_map[other_port])

    data = []
    for port in ports:
        is_present, index_in_data = is_command_already_present(data, port)
        if is_present and index_in_data is not None:
            command_to_update = data[index_in_data]
            command_to_update[2] = command_to_update[2] | ((vlan_miim_register_map[port]['data'] << vlan_miim_register_map[port]['offset']) & 0xFF)
            command_to_update[3] = command_to_update[3] | (((vlan_miim_register_map[port]['data'] << vlan_miim_register_map[port]['offset']) & 0xFF00) >> vlan_miim_register_map[port]['offset'])
            data[index_in_data] = command_to_update
        else:
            command = []
            if vlan_miim_register_map[port]['data'] != vlan_miim_register_map[port]['sys_default']:
                command = [
                    vlan_miim_register_map[port]['phy'],
                    vlan_miim_register_map[port]['reg'],
                    (vlan_miim_register_map[port]['data'] << vlan_miim_register_map[port]['offset']) & 0xFF,
                    ((vlan_miim_register_map[port]['data'] << vlan_miim_register_map[port]['offset']) & 0xFF00) >> vlan_miim_register_map[port]['offset'],
                ]
                data.append(command)

    return data
