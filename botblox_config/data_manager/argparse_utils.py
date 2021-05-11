import argparse
from argparse import Action, ArgumentParser, Namespace
from enum import Enum
from typing import Any, AnyStr, Callable, Dict, List, Sequence, Union


def _copy_items(items: Union[List, Dict]) -> Union[List, Dict]:
    if items is None:
        return []
    if type(items) is list:
        return items[:]
    import copy
    return copy.copy(items)


def add_multi_argument(parser: Union[Action, ArgumentParser],  # noqa: C901
                       short: AnyStr,
                       long: AnyStr,
                       names: Sequence[AnyStr],
                       types: Sequence[Union[type, Callable[[AnyStr], Any]]],
                       action: str = "store",
                       **kwargs: Any) -> None:

    if not isinstance(names, Sequence) or not isinstance(types, Sequence) or len(names) != len(types):
        raise ValueError("names and type fields have to be lists of same length")
    nargs = len(names)

    class MultiArgument(argparse.Action):
        def __call__(self,
                     arg_parser: Union[ArgumentParser, Action],
                     namespace: Namespace,
                     values: List[AnyStr],
                     option_string: AnyStr = None) -> None:
            if not isinstance(values, list) or len(values) != nargs:
                raise argparse.ArgumentError(self, 'argument "{}" requires {} values'.format(self.dest, nargs))

            for i in range(nargs):
                try:
                    values[i] = types[i](values[i])
                except ValueError as e:
                    if isinstance(types[i], type) and issubclass(types[i], Enum):
                        raise argparse.ArgumentError(self,
                                                     'Wrong value "{}" of argument "{}", allowed values are {{{}}}'.
                                                     format(values[i], names[i], ",".join(types[i]._member_names_)))
                    if len(e.args) == 0 or len(e.args[0]) == 0:
                        raise argparse.ArgumentError(self, 'Wrong type of argument "{}"'.format(names[i]))
                    else:
                        raise argparse.ArgumentError(self, 'Error in argument "{}": {}'.format(names[i], str(e)))

            if action == "store":
                setattr(namespace, self.dest, values)
            elif action == "append":
                items = getattr(namespace, self.dest, None)
                items = _copy_items(items)
                items.append(values)
                setattr(namespace, self.dest, items)

    parser.add_argument(
        short, long,
        nargs=nargs,
        action=MultiArgument,
        type=str,
        metavar=tuple(map(str.upper, names)),
        **kwargs
    )
