import argparse
from enum import Enum
from typing import AnyStr, Sequence, Callable, Any, Union


def _copy_items(items):
    if items is None:
        return []
    if type(items) is list:
        return items[:]
    import copy
    return copy.copy(items)


class IntRange:
    def __init__(self, min: Union[int, None], max: Union[int, None], name: AnyStr = "value"):
        self._min = min
        self._max = max
        self._name = name

    def __call__(self, value) -> int:
        num = int(value)
        if (self._min is not None and num < self._min) or (self._max is not None and num > self._max):
            raise ValueError("{} has to be in range {}-{}".format(self._name, self._min, self._max))
        return num

    def __repr__(self):
        return "{}({},{})".format(self._name if self._name is not None and len(self._name) > 0 else "Range", self._min, self._max)


def add_multi_argument(parser,
                       short: AnyStr,
                       long: AnyStr,
                       names: Sequence[AnyStr],
                       types: Sequence[Callable[[AnyStr], Any]],
                       action: str = "store",
                       **kwargs):

    if not isinstance(names, Sequence) or not isinstance(types, Sequence) or len(names) != len(types):
        raise ValueError("names and type fields have to be lists of same length")
    nargs = len(names)

    class MultiArgument(argparse.Action):
        def __call__(self, _, namespace, values, option_string=None):
            if not isinstance(values, list) or len(values) != nargs:
                raise argparse.ArgumentError(self, 'argument "{}" requires {} values'.format(self.dest, nargs))

            for i in range(nargs):
                try:
                    values[i] = types[i](values[i])
                except ValueError as e:
                    if isinstance(types[i], type) and issubclass(types[i], Enum):
                        raise argparse.ArgumentError(self, 'Wrong value "{}" of argument "{}", allowed values are {{{}}}'.format(values[i], names[i], ",".join(types[i]._member_names_)))
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