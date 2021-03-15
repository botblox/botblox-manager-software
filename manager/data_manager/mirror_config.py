from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)


class PortMirrorConfig:
    _default_miim_register_map = {
        'enable': {
            'name': 'PORT_MIRROR_EN',
            'phy': 20,
            'reg': 3,
            'number_of_bits': 1,
            'offset': 15,
            'sys_default': 0,
            'data': -1,
            'choice_mapping': {
                True: 1,
                False: 0,
            }
        },
        'mode': {
            'name': 'PORT_MIRROR_MODE',
            'phy': 20,
            'reg': 3,
            'number_of_bits': 2,
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
            'number_of_bits': 8,
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
            'number_of_bits': 3,
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
            'number_of_bits': 8,
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
        }
    }

    _default_config_options = {
        'mirror_port': None,
        'mode': None,
        'rx_port': None,
        'tx_port': None,
        'reset': None,
        'enable': False,
    }

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
        option_name: str,
    ) -> Tuple[bool, int]:
        if self.commands != []:
            for index, command in enumerate(self.commands):
                option_phy = self.miim_register_map[option_name]['phy']
                option_reg = self.miim_register_map[option_name]['reg']

                if option_phy == command[0] and option_reg == command[1]:
                    return (True, index)
        return (False, -1)

    def update_existing_command(
        self,
        option_name: str,
        index_of_command_to_update: int,
        option: Optional[Union[int, str, List[int]]] = None,
        use_default: bool = False,
    ) -> None:
        command_to_update: List[int] = self.commands[index_of_command_to_update]

        option_data: int = 0
        option_bits_offset: int = self.miim_register_map[option_name]['offset']

        if not use_default:
            option_choice_mapping = self.miim_register_map[option_name]['choice_mapping']

            if isinstance(option, str) or isinstance(option, int):
                option_data = option_choice_mapping[option]
            elif isinstance(option, list):
                for each_option in option:
                    option_data = option_data | option_choice_mapping[each_option]
        else:
            assert use_default is True
            option_data = self.miim_register_map[option_name]['sys_default']

        command_to_update[2] = command_to_update[2] | ((option_data << option_bits_offset) & 0xFF)
        command_to_update[3] = command_to_update[3] | (((option_data << option_bits_offset) & 0xFF00) >> 8)

        self.commands[index_of_command_to_update] = command_to_update
        return

    def create_new_command(
        self,
        option_name: str,
        option: Optional[Union[int, str, List[int]]] = None,
        use_default: bool = False,
    ) -> None:
        option_data: int = 0
        option_bits_offset = self.miim_register_map[option_name]['offset']

        if not use_default:
            option_choice_mapping = self.miim_register_map[option_name]['choice_mapping']
            option_data = 0

            if isinstance(option, str) or isinstance(option, int):
                option_data = option_choice_mapping[option]
            elif isinstance(option, list):
                for each_option in option:
                    option_data = option_data | option_choice_mapping[each_option]
        else:
            assert use_default is True
            option_data = self.miim_register_map[option_name]['sys_default']

        command = [
            self.miim_register_map[option_name]['phy'],
            self.miim_register_map[option_name]['reg'],
            (option_data << option_bits_offset) & 0xFF,
            ((option_data << option_bits_offset) & 0xFF00) >> 8,
        ]
        self.commands.append(command)
        return

    def add_command_for_option_default(
        self,
        option_name: str,
        is_reset_mode: bool = False,
    ) -> None:
        if not is_reset_mode:
            assert self.config_options[option_name] is None
        assert option_name in self.miim_register_map.keys()

        is_command_exist: Tuple[bool, int] = self.is_command_already_present(option_name)
        if is_command_exist[0]:
            command_index: int = is_command_exist[1]
            self.update_existing_command(option_name, command_index, None, use_default=True)
        else:
            assert is_command_exist[0] is False
            self.create_new_command(option_name, None, use_default=True)

        return

    def create_configuration(
        self,
    ) -> List[List[int]]:
        if self.config_options['reset']:
            for option_name in self.config_options.keys():
                if option_name in self.miim_register_map.keys():
                    self.add_command_for_option_default(option_name, is_reset_mode=True)
                else:
                    assert ValueError('Could not find option in register map')
            else:
                return self.commands

        assert not self.config_options['reset']

        for option_name, option in self.config_options.items():
            if option_name == 'reset':
                continue

            assert option_name != 'reset'
            if option is None:
                self.add_command_for_option_default(option_name)
                continue

            is_command_exist = self.is_command_already_present(option_name)

            if is_command_exist[0]:
                command_index: int = is_command_exist[1]
                self.update_existing_command(option_name, command_index, option)
            else:
                assert is_command_exist[0] is False
                self.create_new_command(option_name, option)
        else:
            return self.commands
