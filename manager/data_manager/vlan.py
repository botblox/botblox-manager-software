from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    TypedDict,
    Union,
    Set,
)
from functools import reduce


class VlanConfig:
    _default_miim_register_map = {
        1: {
            'name': 'PBV_MEMBER_P0',
            'phy': 23,
            'reg': 16,
            'size': 8,
            'offset': 0,
            'sys_default': 0xFF,
            'data': 0,
            'choice_mapping': {
                1: 0b00000010,
            }
        },
        2: {
            'name': 'PBV_MEMBER_P1',
            'phy': 23,
            'reg': 16,
            'size': 8,
            'offset': 8,
            'sys_default': 0xFF,
            'data': 0,
            'choice_mapping': {
                2: 0b00000100,
            }
        },
        3: {
            'name': 'PBV_MEMBER_P2',
            'phy': 23,
            'reg': 17,
            'size': 8,
            'offset': 0,
            'sys_default': 0xFF,
            'data': 0,
            'choice_mapping': {
                3: 0b00001000,
            }
        },
        4: {
            'name': 'PBV_MEMBER_P3',
            'phy': 23,
            'reg': 18,
            'size': 8,
            'offset': 0,
            'sys_default': 0xFF,
            'data': 0,
            'choice_mapping': {
                4: 0b01000000,
            }
        },
        5: {
            'name': 'PBV_MEMBER_P4',
            'phy': 23,
            'reg': 18,
            'size': 8,
            'offset': 8,
            'sys_default': 0xFF,
            'data': 0,
            'choice_mapping': {
                5: 0b10000000,
            }
        },
    }

    class ConfigOptions(TypedDict):
        group: Optional[List[List[int]]]
        reset: bool

    _default_config_options: ConfigOptions = {
        'group': None,
        'reset': False,
    }

    # _vlan_binary_offset_map = {
    #     1: 2,
    #     2: 3,
    #     3: 4,
    #     4: 6,
    #     5: 7,
    # }

    _default_commands: List[List[int]] = []

    def __init__(
        self,
        args: Tuple,
    ) -> None:
        self.miim_register_map = dict(self._default_miim_register_map)
        self.commands = list(self._default_commands)

        cli_options: Dict = vars(args)

        self.config_options = dict(self._default_config_options)
        for cli_option in cli_options.keys():
            if cli_option in self.config_options.keys():
                self.config_options[cli_option] = cli_options[cli_option]

        # Now we can add any extra config that wasn't present in the cli arguments
        # This is for options in the datasheet that we always want to be set but don't offer as configuration on the cli
        if not cli_options.get('reset'):
            self.config_options['enable'] = True

    def is_command_already_present(
        self,
        port: int,
    ) -> Tuple[bool, int]:
        if self.commands != []:
            option_phy = self.miim_register_map[port]['phy']
            option_reg = self.miim_register_map[port]['reg']

            for index, command in enumerate(self.commands):
                if option_phy == command[0] and option_reg == command[1]:
                    return (True, index)
        return (False, -1)

    def update_existing_command(
        self,
        index_of_command_to_update: int,
        port: int,
        vlan_members_for_port: List[int] = [],
        use_default: bool = False,
    ) -> None:
        command_to_update: List[int] = self.commands[index_of_command_to_update]

        command_data: int = 0  # come up with a better name
        options_bits_offset: int = self.miim_register_map[port]['offset']

        if not use_default:
            # COULD PROBABLY FACTOR THIS OUT INTO SEPARATE STATIC METHOD>>>>>
            def add_port_to_vlan_membership_in_register_data(
                data: int,
                port: int,
            ) -> int:
                return data | self.miim_register_map[port]['choice_mapping'][port]
            command_data = reduce(
                function=add_port_to_vlan_membership_in_register_data,
                sequence=vlan_members_for_port,
                initial=0,
            ) 
        else:
            command_data = self.miim_register_map[port]['sys_default']

        command_to_update[2] = command_to_update[2] | ((command_data << options_bits_offset) & 0xFF)
        command_to_update[2] = command_to_update[3] | (((command_data << options_bits_offset) & 0xFF00) >> 8)

        self.commands[index_of_command_to_update] = command_to_update
        return None

    def create_new_command(
        self,
        port: int,
        vlan_members_for_port: List[int] = [],
        use_default: bool = False,
    ) -> None:
        command_data: int = 0
        command_data_binary_offset = self.miim_register_map[port]['offset']

        if not use_default:
            def add_port_to_vlan_membership_in_register_data(
                data: int,
                port: int,
            ) -> int:
                return data | self.miim_register_map[port]['choice_mapping'][port]
            command_data = reduce(
                function=add_port_to_vlan_membership_in_register_data,
                sequence=vlan_members_for_port,
                initial=0,
            )
        else:
            command_data = self.miim_register_map[port]['sys_default']

        command = [
            self.miim_register_map[port]['phy'],
            self.miim_register_map[port]['reg'],
            (command_data << command_data_binary_offset) & 0xFF,
            ((command_data << command_data_binary_offset) & 0xFF00) >> 8,
        ]

        self.commands.append(command)
        return None

    def add_command_for_option_default(
        self,
        port: int,
    ) -> None:
        is_command_exists = self.is_command_already_present(port)
        if is_command_exists[0]:
            command_index: int = is_command_exists[1]
            # self.update_existing_command(command_index, port=port, binary_offset=binary_offset, use_default=True)
            self.update_existing_command(command_index, port=port, use_default=True)
        else:
            self.create_new_command(port=port, use_default=True)

        return None

    def create_configuration(
        self,
    ) -> List[List[int]]:
        if self.config_options['reset']:
            for port in self.miim_register_map.keys():
                self.add_command_for_option_default(port, is_default=True)
            else:
                return self.commands

        # Code that will take the groups and calculate the data
        groupings = self.config_options['group']

        # We should loop through all ports and find their partners
        for port in self.miim_register_map.keys():
            
            groupings_with_port: List[List[int]] = filter(lambda grouping: port in grouping, groupings)
            if groupings[0] != []:
                # We know that the user specified this port in the cli

                # May contain duplicates
                vlan_members_for_port: List[int] = reduce(
                    lambda vlan_members, grouping: vlan_members + grouping,
                    groupings_with_port,
                )

                is_command_exists = self.is_command_already_present(port)

                if is_command_exists[0]:
                    command_index: int = is_command_exists[1]
                    self.update_existing_command(
                        command_index=command_index,
                        port=port,
                        vlan_members_for_port=vlan_members_for_port,
                    )
                else:
                    self.create_new_command(
                        port=port,
                        vlan_members_for_port=vlan_members_for_port,
                    )
                # We probably want to pass port and vlan_members_for_port to create_new_command or update_existing_command
                # I think we are going to have to very carefully consider naming conventions here and in mirror config
            else:
                # Want to use the default
                self.add_command_for_option_default(port)
                continue