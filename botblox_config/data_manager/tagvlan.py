import functools
import logging
from argparse import Action, Namespace, SUPPRESS
from collections import defaultdict
from enum import Enum
from typing import (cast, Dict, List, Optional, Union)

from .argparse_utils import add_multi_argument
from .switch_config import SwitchConfig, SwitchConfigCLI
from ..switch import Port
from ..switch.fields import BitField, BitsField, PortListField, ShortField
from ..switch.ip175g import IP175G
from ..switch.switch import SwitchChip, SwitchFeature


class VLAN:
    """
    A VLAN table entry representation.
    """
    def __init__(self, vlan_id: int, members: List[Port] = None) -> None:
        self.vlan_id: int = vlan_id
        self.members: List[Port] = members if members is not None else list()


class VLANMode(Enum):
    """
    VLAN mode specifies how the switch handles packets based on their assigned VLAN ID.
    """
    DISABLED = "DISABLED"  # VLAN ID is ignored
    OPTIONAL = "OPTIONAL"  # VLAN ID handled, VLAN ID does not need to be in VLAN table
    ENABLED = "ENABLED"  # VLAN ID handled, VLAN ID needs to be in VLAN table
    STRICT = "STRICT"  # VLAN ID handled, VLAN ID needs to be in VLAN table for the specific inbound port

    def __str__(self) -> None:
        return self.value


class VLANHeaderAction(Enum):
    """
    What to do with the 802.1Q header of outgoing packets.
    """
    KEEP = "KEEP"  # Keep the header as it was in the packet on ingress.
    ADD = "ADD"  # Always add 802.1Q header to outgoing packets.
    STRIP = "STRIP"  # Remove the 802.1Q header from all outgoing packets.

    def __str__(self) -> None:
        return self.value


class VLANReceiveMode(Enum):
    """
    What to do with tagged/untagged ingress packets.
    """
    ANY = "ANY"  # allow receiving both tagged and untagged packets
    ONLY_TAGGED = "ONLY_TAGGED"  # allow receiving only tagged packets
    ONLY_UNTAGGED = "ONLY_UNTAGGED"  # allow receiving only untagged packets

    def __str__(self) -> None:
        return self.value


class VLANPortConfig:
    """
    Port-related configuration of VLANs.
    """
    def __init__(self,
                 port: Port,
                 default_vlan_id: Optional[int] = None,
                 mode: Optional[VLANMode] = None,
                 force_vlan_id: Optional[bool] = None,
                 receive_mode: Optional[VLANReceiveMode] = None,
                 header_action: Optional[VLANHeaderAction] = None,
                 per_vlan_header_action: Optional[Dict[int, VLANHeaderAction]] = None) -> None:
        self.port: Port = port
        self.default_vlan_id: Optional[int] = default_vlan_id
        self.mode: Optional[VLANMode] = mode
        self.force_vlan_id: Optional[bool] = force_vlan_id
        self.receive_mode: Optional[VLANReceiveMode] = receive_mode
        self.header_action: Optional[VLANHeaderAction] = header_action
        self.per_vlan_header_action: Optional[Dict[int, VLANHeaderAction]] = per_vlan_header_action


class TagVlanConfig(SwitchConfig):
    """
    Configuration of Tagged VLANs.
    """
    def __init__(self, switch: SwitchChip) -> None:
        super().__init__(switch)

        self._vlan_mode: Optional[VLANMode] = None
        self._force_vlan_id: Optional[bool] = None
        self._receive_mode: Optional[VLANReceiveMode] = None
        self._header_action: Optional[VLANHeaderAction] = None

        self._vlans: Dict[int, VLAN] = dict()
        self._port_configs: List[VLANPortConfig] = [VLANPortConfig(p) for p in self._ports()]

        self._reset = False

    def set_all_port_vlan_mode(self, mode: VLANMode) -> None:
        self._check_supports_vlan_mode(mode)
        self._vlan_mode = mode

    def set_all_port_force_vlan_id(self, force: bool) -> None:
        self._switch.check_feature(SwitchFeature.VLAN_FORCE)
        self._force_vlan_id = force

    def set_all_port_receive_mode(self, mode: VLANReceiveMode) -> None:
        self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
        self._receive_mode = mode

    def set_all_port_header_action(self, action: VLANHeaderAction) -> None:
        self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
        self._header_action = action

    def set_port_config(self,
                        port: Port,
                        default_vlan_id: Optional[int] = None,
                        mode: Optional[VLANMode] = None,
                        force_vlan_id: Optional[bool] = None,
                        receive_mode: Optional[VLANReceiveMode] = None,
                        header_action: Optional[VLANHeaderAction] = None,
                        per_vlan_header_action: Optional[Dict[int, VLANHeaderAction]] = None) -> None:
        port_config = self._port_configs[self._ports().index(port)]
        if default_vlan_id is not None:
            self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
            self._switch.check_vlan_id(default_vlan_id)
            port_config.default_vlan_id = default_vlan_id
        if mode is not None:
            self._check_supports_per_port_vlan_mode(mode)
            port_config.mode = mode
        if force_vlan_id is not None:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_FORCE)
            port_config.force_vlan_id = force_vlan_id
        if receive_mode is not None:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_RECEIVE_MODE)
            port_config.receive_mode = receive_mode
        if header_action is not None:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_HEADER_ACTION)
            port_config.header_action = header_action
        if per_vlan_header_action:
            self._switch.check_feature(SwitchFeature.PER_VLAN_HEADER_ACTION)
            port_config.per_vlan_header_action = per_vlan_header_action

    def add_vlan(self, vlan_id: int) -> VLAN:
        self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
        self._switch.check_feature(SwitchFeature.VLAN_TABLE)
        self._switch.check_vlan_id(vlan_id)
        if vlan_id not in self._vlans:
            if len(self._vlans) >= self._switch.max_vlans():
                raise RuntimeError("{} can only handle {} VLANs, but more were requested",
                                   self._switch.name(), self._switch.max_vlans())
            vlan = VLAN(vlan_id)
            self._vlans[vlan_id] = vlan
            return vlan
        else:
            return self._vlans[vlan_id]

    def remove_vlan(self, vlan_id: int) -> None:
        self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
        self._switch.check_feature(SwitchFeature.VLAN_TABLE)

        if vlan_id in self._vlans:
            del self._vlans[vlan_id]

    def add_vlan_member(self, vlan: Union[int, VLAN], port: Port) -> None:
        self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
        self._switch.check_feature(SwitchFeature.VLAN_TABLE)
        if isinstance(vlan, int):
            if vlan not in self._vlans:
                vlan = self.add_vlan(vlan)
            else:
                vlan = self._vlans[vlan]
        if port not in vlan.members:
            vlan.members.append(port)

    def remove_vlan_member(self, vlan: Union[int, VLAN], port: Port) -> None:
        self._switch.check_feature(SwitchFeature.TAGGED_VLAN)
        self._switch.check_feature(SwitchFeature.VLAN_TABLE)
        if isinstance(vlan, int):
            if vlan not in self._vlans:
                vlan = self.add_vlan(vlan)
        if port in vlan.members:
            vlan.members.remove(port)

    def set_port_vlan_header_action(self, vlan: int, port: Port, action: VLANHeaderAction) -> None:
        port_config = self._port_configs[self._ports().index(port)]
        if port_config.per_vlan_header_action is None:
            port_config.per_vlan_header_action = dict()
        port_config.per_vlan_header_action[vlan] = action

    def reset(self) -> None:
        self._reset = True

    def _check_supports_per_port_vlan_mode(self, mode: VLANMode) -> None:
        if mode == VLANMode.DISABLED:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_MODE_DISABLE)
        elif mode == VLANMode.OPTIONAL:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_MODE_OPTIONAL)
        elif mode == VLANMode.ENABLED:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_MODE_ENABLE)
        elif mode == VLANMode.STRICT:
            self._switch.check_feature(SwitchFeature.PER_PORT_VLAN_MODE_STRICT)

    def _check_supports_vlan_mode(self, mode: VLANMode) -> None:
        if mode == VLANMode.OPTIONAL:
            self._switch.check_feature(SwitchFeature.VLAN_MODE_OPTIONAL)
        elif mode == VLANMode.ENABLED:
            self._switch.check_feature(SwitchFeature.VLAN_MODE_ENABLE)
        elif mode == VLANMode.STRICT:
            self._switch.check_feature(SwitchFeature.VLAN_MODE_STRICT)

    def apply_to_switch(self) -> None:
        if isinstance(self._switch, IP175G):
            self._apply_to_switch_ip175g()
        else:
            raise NotImplementedError()

    def _apply_to_switch_ip175g(self) -> None:  # noqa: C901
        assert isinstance(self._switch, IP175G)

        if self._reset:
            cast(PortListField, self._switch.fields["TAG_VLAN_EN"]).clear()
            cast(BitField, self._switch.fields["UNVID_MODE"]).set_value(True)
            cast(BitField, self._switch.fields["VLAN_TABLE_CLR"]).set_value(True)
            cast(BitsField, self._switch.fields["ACCEPTABLE_FRM_TYPE"]).set_value(0)
            cast(PortListField, self._switch.fields["ADD_TAG"]).clear()
            cast(PortListField, self._switch.fields["REMOVE_TAG"]).clear()
            cast(BitsField, self._switch.fields["VLAN_VALID"]).set_value(0)
            return

        if len(self._vlans) > 0:
            cast(BitsField, self._switch.fields["VLAN_VALID"]).set_value(int(pow(2, len(self._vlans) - 1)))

        i = 0
        for vlan in self._vlans.values():
            vlan_i = "{:1X}".format(i)
            cast(BitsField, self._switch.fields["VID_" + vlan_i]).set_value(vlan.vlan_id)
            if len(vlan.members) > 0:
                cast(PortListField, self._switch.fields["VLAN_MEMBER_" + vlan_i]).clear()
                for port in vlan.members:
                    cast(PortListField, self._switch.fields["VLAN_MEMBER_" + vlan_i]).add_port(port)
            i += 1

        acceptable_frm_type = None
        if self._receive_mode == VLANReceiveMode.ANY:
            acceptable_frm_type = 0
        elif self._receive_mode == VLANReceiveMode.ONLY_TAGGED:
            acceptable_frm_type = 1
        elif self._receive_mode == VLANReceiveMode.ONLY_UNTAGGED:
            acceptable_frm_type = 2
        if acceptable_frm_type is not None:
            cast(BitsField, self._switch.fields["ACCEPTABLE_FRM_TYPE"]).set_value(acceptable_frm_type)

        all_mode = self._vlan_mode
        unvid_mode = all_mode
        unvid_mode_error = False
        all_force_vlan_id = self._force_vlan_id
        all_header_action = self._header_action
        for port_config in self._port_configs:
            port_i = self._ports().index(port_config.port)
            port_mode = all_mode
            if port_config.mode is not None:
                port_mode = port_config.mode
            if port_mode == VLANMode.DISABLED:
                cast(PortListField, self._switch.fields["TAG_VLAN_EN"]).remove_port(port_config.port)
                if unvid_mode is not None and unvid_mode == False:  # noqa: E712
                    unvid_mode_error = True
                else:
                    unvid_mode = True
                    cast(BitField, self._switch.fields["UNVID_MODE"]).set_value(unvid_mode)
            elif port_mode == VLANMode.OPTIONAL:
                cast(PortListField, self._switch.fields["TAG_VLAN_EN"]).add_port(port_config.port)
                if unvid_mode is not None and unvid_mode == False:  # noqa: E712
                    unvid_mode_error = True
                else:
                    unvid_mode = True
                    cast(BitField, self._switch.fields["UNVID_MODE"]).set_value(unvid_mode)
            elif port_mode == VLANMode.ENABLED:
                cast(PortListField, self._switch.fields["TAG_VLAN_EN"]).add_port(port_config.port)
                cast(PortListField, self._switch.fields["VLAN_INGRESS_FILTER"]).remove_port(port_config.port)
                if unvid_mode is not None and unvid_mode == True:  # noqa: E712
                    unvid_mode_error = True
                else:
                    unvid_mode = False
                    cast(BitField, self._switch.fields["UNVID_MODE"]).set_value(unvid_mode)
            elif port_mode == VLANMode.STRICT:
                cast(PortListField, self._switch.fields["TAG_VLAN_EN"]).add_port(port_config.port)
                cast(PortListField, self._switch.fields["VLAN_INGRESS_FILTER"]).add_port(port_config.port)
                if unvid_mode is not None and unvid_mode == True:  # noqa: E712
                    unvid_mode_error = True
                else:
                    unvid_mode = False
                    cast(BitField, self._switch.fields["UNVID_MODE"]).set_value(unvid_mode)

            # unfortunately, UNVID_MODE cannot be set port-wise, so there are limitations on the combinations
            if unvid_mode_error:
                raise ValueError("Switchblox can only have all its ports in mode DISABLED/OPTIONAL or all in "
                                 "ENABLED/STRICT, but not a combination of these two groups.")

            if port_config.default_vlan_id is not None:
                cast(ShortField, self._switch.fields["VLAN_INFO_" + str(port_i)]).set_value(port_config.default_vlan_id)

            force_vlan_id = all_force_vlan_id
            if port_config.force_vlan_id is not None:
                force_vlan_id = port_config.force_vlan_id
            if force_vlan_id is not None:
                cast(PortListField, self._switch.fields["VLAN_CLS"]).set_port(port_config.port, force_vlan_id)

            header_action = all_header_action
            if port_config.header_action is not None:
                header_action = port_config.header_action
            if header_action == VLANHeaderAction.KEEP:
                cast(PortListField, self._switch.fields["ADD_TAG"]).remove_port(port_config.port)
                cast(PortListField, self._switch.fields["REMOVE_TAG"]).remove_port(port_config.port)
            elif header_action == VLANHeaderAction.ADD:
                cast(PortListField, self._switch.fields["ADD_TAG"]).add_port(port_config.port)
                cast(PortListField, self._switch.fields["REMOVE_TAG"]).remove_port(port_config.port)
            elif header_action == VLANHeaderAction.STRIP:
                cast(PortListField, self._switch.fields["ADD_TAG"]).remove_port(port_config.port)
                cast(PortListField, self._switch.fields["REMOVE_TAG"]).add_port(port_config.port)


class TagVlanConfigCLI(SwitchConfigCLI):
    """
    CLI parser for the tag-vlan command.
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        super().__init__(subparsers, switch)

        self._subparser = self._subparsers.add_parser(
            "tag-vlan",
            help="Configure tagged VLAN",
        )

        vlan_range = functools.partial(self._switch.parse_vlan_id)
        vlan_range.__name__ = "VLAN ID"
        port_arg = functools.partial(self._switch.get_port)
        port_arg.__name__ = "port"
        port_names = tuple(self._switch.port_names())
        port_description = "port{{{}}}".format(",".join(port_names))

        self._subparser.add_argument(
            '-D', '--default-vlan',
            type=vlan_range,
            required=False,
            default=SUPPRESS,
            help='''Define default VLAN for all ports. Can be overridden per port by --port-default-vlan.'''
        )
        add_multi_argument(
            self._subparser,
            '-d', '--port-default-vlan',
            names=(port_description, "default_vlan"),
            types=(port_arg, vlan_range),
            action="append",
            required=False,
            help='''Define default VLAN for the given port. E.g. "--port-default-vlan 1 2" sets port 1
                    to assign untagged packets to VLAN 2. Overrides --default-vlan for the given port.'''
        )
        self._subparser.add_argument(
            '-M', '--vlan-mode',
            type=VLANMode,
            choices=list(VLANMode),
            required=False,
            help='''Define default VLAN mode for all ports. Can be overridden per port by --port-vlan-mode.
                    DISABLED: Ports do not use VLAN information for switching decisions.
                    OPTIONAL: Packets from VLANs not in VLAN table are handled.
                    ENABLED: Packets from VLANs not in VLAN table are dropped.
                    STRICT: Same as ENABLED, but also checks ingress port in VLAN table.'''
        )
        if self._switch.has_feature(SwitchFeature.PER_PORT_VLAN_MODE):
            add_multi_argument(
                self._subparser,
                '-m', '--port-vlan-mode',
                names=(port_description, "vlan_mode"),
                types=(port_arg, VLANMode),
                action="append",
                required=False,
                help='''Define default VLAN mode for the given port. Overrides --vlan-mode for the given port.
                        DISABLED: This port does not use VLAN information for switching decisions.
                        OPTIONAL: Packets from VLANs not in VLAN table are handled.
                        ENABLED: Packets from VLANs not in VLAN table are dropped.
                        STRICT: Same as ENABLED, but also checks ingress port in VLAN table.'''
            )
        if self._switch.has_feature(SwitchFeature.PER_PORT_VLAN_FORCE):
            self._subparser.add_argument(
                '-f', '--force-vlan-id',
                nargs="*",
                type=port_arg,
                required=False,
                choices=self._switch.ports() if self._switch is not None else None,
                metavar=(port_description, port_description),
                help='''Set VLAN ID forcing for the listed ports. If VLAN ID is forced on a port,
                        all ingress traffic from the port is treated as having VLAN ID equal to
                        the port's default VLAN ID, regardless of the actual tag in the packet.
                        Using the argument with no ports means to force VLAN ID on all ports.'''
            )
        self._subparser.add_argument(
            '-T', '--receive-mode',
            type=VLANReceiveMode,
            choices=list(VLANReceiveMode),
            required=False,
            help='''Define VLAN receive mode for all ports. Can be overridden per port by --port-receive-mode.
                    ANY: All ingress packets are accepted.
                    ONLY_TAGGED: Only packets with VLAN tag are accepted.
                    ONLY_UNTAGGED: Only packets without VLAN tag are accepted.'''
        )
        if self._switch.has_feature(SwitchFeature.PER_PORT_VLAN_RECEIVE_MODE):
            add_multi_argument(
                self._subparser,
                '-t', '--port-receive-mode',
                names=(port_description, "receive_mode"),
                types=(port_arg, VLANReceiveMode),
                action="append",
                required=False,
                help='''Define VLAN receive mode for the given port. Overrides --receive-mode for the port.
                        ANY: All ingress packets are accepted.
                        ONLY_TAGGED: Only packets with VLAN tag are accepted.
                        ONLY_UNTAGGED: Only packets without VLAN tag are accepted.'''
            )
        self._subparser.add_argument(
            '-A', '--header-action',
            type=VLANHeaderAction,
            choices=list(VLANHeaderAction),
            required=False,
            help='''Define header action for all ports. Can be overridden per port by --port-header-action.
                    KEEP: Keep VLAN tag if the packet had it on ingress, do not add it if the packet did not have it.
                    ADD: Add VLAN tag to all packets leaving the switch.
                    STRIP: Remove VLAN tag from all packets leaving the switch.'''
        )
        if self._switch.has_feature(SwitchFeature.PER_PORT_VLAN_HEADER_ACTION):
            add_multi_argument(
                self._subparser,
                '-a', '--port-header-action',
                names=(port_description, 'header_action'),
                types=(port_arg, VLANHeaderAction),
                action="append",
                required=False,
                help='''Define header action for the given port. Overrides --header-action for the port.
                        KEEP: Keep VLAN tag if the packet had it on ingress, do not add it if the packet did not have it
                        ADD: Add VLAN tag to all packets leaving the port.
                        STRIP: Remove VLAN tag from all packets leaving the port.'''
            )
        if self._switch.has_feature(SwitchFeature.PER_VLAN_HEADER_ACTION):
            add_multi_argument(
                self._subparser,
                '-p', '--port-vlan-header-action',
                names=(port_description, "vlan", "header_action"),
                types=(port_arg, vlan_range, VLANHeaderAction),
                action="append",
                required=False,
                help='''Define header action for the given port and VLAN ID.
                        Overrides --header-action and --port-header-action for the port and VLAN ID.
                        KEEP: Keep VLAN tag if the packet had it on ingress, do not add it if the packet did not have it
                        ADD: Add VLAN tag to all packets leaving the port.
                        STRIP: Remove VLAN tag from all packets leaving the port.'''
            )

        if self._switch.has_feature(SwitchFeature.VLAN_TABLE):
            self._subparser.add_argument(
                '-v', '--vlan',
                nargs='+',
                type=str,
                action='append',
                required=False,
                metavar=('VLAN', port_description),
                help='''Define a VLAN table entry. First argument is the VLAN ID and following arguments
                        are ports that are members of the VLAN.'''
            )

        self._subparser.add_argument(
            '-r',
            '--reset',
            action='store_true',
            default=SUPPRESS,
            help='Reset the tagged VLAN configuration to default'
        )

        def execute(args: Namespace) -> TagVlanConfigCLI:
            try:
                return self.apply(args)
            except Exception as e:
                self._subparser.error(str(e))
        self._subparser.set_defaults(execute=execute)

    def apply(self, args: Namespace) -> 'TagVlanConfigCLI':  # noqa: C901
        cli_options: Dict = vars(args)
        config = TagVlanConfig(self._switch)

        def has_option(option: str) -> bool:
            return cli_options.get(option, None) is not None

        if has_option('reset'):
            config.reset()
            config.apply_to_switch()
            return self

        if has_option('default_vlan') or has_option('port_default_vlan'):
            default_vlan = cli_options.get('default_vlan', None)
            port_default_vlan = cli_options.get('port_default_vlan', None)
            port_options = dict(port_default_vlan if port_default_vlan is not None else list())
            for port in self._switch.ports():
                port_vlan = port_options.get(port, default_vlan)
                if port_vlan is not None:
                    config.set_port_config(port, default_vlan_id=port_vlan)

        if has_option('vlan_mode'):
            config.set_all_port_vlan_mode(cli_options['vlan_mode'])
        if has_option('port_vlan_mode'):
            port_options = dict(cli_options['port_vlan_mode'])
            for port in set(self._switch.ports()).intersection(port_options.keys()):
                config.set_port_config(port, mode=port_options[port])

        if has_option('force_vlan_id'):
            force_vlan_id = cli_options.get('force_vlan_id')
            if len(force_vlan_id) == 0:
                config.set_all_port_force_vlan_id(True)
            else:
                for port in self._switch.ports():
                    force = port in force_vlan_id
                    if force:
                        config.set_port_config(port, force_vlan_id=True)

        if has_option('receive_mode'):
            config.set_all_port_receive_mode(cli_options['receive_mode'])
        if has_option('port_receive_mode'):
            port_options = dict(cli_options['port_receive_mode'])
            for port in set(self._switch.ports()).intersection(port_options.keys()):
                config.set_port_config(port, receive_mode=port_options[port])

        if has_option('header_action'):
            config.set_all_port_header_action(cli_options['header_action'])
        if has_option('port_header_action'):
            port_options = dict(cli_options['port_header_action'])
            for port in set(self._switch.ports()).intersection(port_options.keys()):
                config.set_port_config(port, header_action=port_options[port])
        if has_option('port_vlan_header_action'):
            port_options = defaultdict(functools.partial(defaultdict, dict))
            for port, vlan, action in cli_options['port_vlan_header_action']:
                port_options[port][vlan] = action
            for port in set(self._switch.ports()).intersection(port_options.keys()):
                for vlan in port_options[port].keys():
                    config.set_port_vlan_header_action(vlan, port, port_options[port][vlan])

        num_vlans = 0
        vlan_configs = cli_options.get('vlan', None)
        for vlan_config in vlan_configs if vlan_configs is not None else list():
            num_vlans += 1
            if num_vlans > self._switch.max_vlans():
                self._subparser.error("Too many VLAN table entries specified. Maximum is {}".format(
                    self._switch.max_vlans()))
            try:
                vlan_id = int(vlan_config[0])
            except ValueError:
                raise self._subparser.error("Wrong VLAN ID.")
            vlan = config.add_vlan(vlan_id)
            for port in vlan_config[1:]:
                config.add_vlan_member(vlan, self._switch.get_port(port))

        config.apply_to_switch()

        for field in self._switch.fields.values():
            if field.is_touched():
                logging.debug(str(field))

        return self

    def create_configuration(self) -> List[List[int]]:
        return self._switch.get_commands(leave_out_default=False, only_touched=True)
