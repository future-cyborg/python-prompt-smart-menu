# -*- coding: utf-8 -*-
"""Parse a command string into arguments."""
import keyword
import re
from typing import Union

from prompt_smart_menu.helpers import InvalidArgError, Kwarg


class InputParser:
    """For parsing a command string into desired types or objects."""

    def __init__(self, *args) -> None:  # noqa: ANN002
        """Initialize with various Cast objects."""
        self._casts = []
        for a in args:
            if not hasattr(a, 'type_cast'):
                raise TypeError(f'Argument must have type_cast() function.')
            self._casts.append(a)
        if not self._casts:
            self._casts = [DefaultCast]

    def _type_cast(self, item: str):  # noqa: ANN
        """Cast types if able."""
        for cast in self._casts:
            item = cast.type_cast(item)
        return item

    def _parse_quotes(self, input_string: str) -> list:
        """Extract a quoted string."""
        delim = input_string[0]
        end_index = input_string.find(delim, 1)
        if end_index == -1:
            raise ValueError(f'No closing quote found in: {input_string}')
        return input_string[1:].split(delim, maxsplit=1)

    def parse(self, input_string: str, recurse: bool = False) -> list:
        """Parse an argument from a command string.

        Args:
            input_string (str): command string to be prased
            recurse (bool): If true, the entire input_string is parsed.
                Otherwise, only the first argument is parsed. Default: False

        Returns:
            list: A list of parsed commands. If recurse=False, the list has
                two items. The first is the parsed argument, the second is
                the remaining command string.
        """
        s = input_string.lstrip()
        if s == '':
            return []

        if s[0] in ['"', "'", '`']:
            split_string = self._parse_quotes(s)
            split_string[1] = split_string[1].lstrip()
            if split_string[1] == '':
                return split_string[0:1]
        else:
            split_string = s.split(maxsplit=1)

        split_string[0] = self._type_cast(split_string[0])
        if len(split_string) == 1 or not recurse:
            return split_string
        else:
            return [split_string[0],
                    *self.parse(split_string[1],
                    recurse=True)]


class DefaultCast:
    """Dummy cast does nothing."""

    @staticmethod
    def type_cast(item: str) -> str:
        """Cast dummy: does nothing."""
        return item


class NumberCast:
    """Cast a string to an int or float following standard python logic.

    - '4' -> int(4)
    - '4.0' -> int(4)

    Will cast a Kwarg's value.
    """

    @classmethod
    def type_cast(cls, item: Union[str, Kwarg]) -> Union[int, float, str]:
        """Cast item, or Kwarg value, to int or float."""
        if isinstance(item, Kwarg):
            item.value(cls._type_cast(item.value()))
        else:
            item = cls._type_cast(item)
        return item

    @staticmethod
    def _type_cast(item: str) -> Union[int, float, str]:
        """Cast item to an int or float."""
        try:
            i = int(item)
            return i
        except (TypeError, ValueError):
            pass
        try:
            f = float(item)
            return f
        except (TypeError, ValueError):
            pass
        return item


class KwargCast:
    r"""Cast a string to be used as a keyword argument.

    String must match the following regex: r'--(\w+)=(.*)'
    The key must also be a valid python identifier.
    """

    kwarg_re = re.compile(r'--(\w+)=(.*)')
    identifier_re = re.compile(r'^[^\d\W]\w*\Z')
    @classmethod
    def type_cast(cls, item: str) -> Kwarg:
        """Cast a string to be used as a keyword argument."""
        if not isinstance(item, str):
            return item
        match = cls.kwarg_re.match(item)
        if not match:
            return item
        key = match.group(1)
        value = match.group(2)
        if not cls.identifier_re.match(key):
            raise InvalidArgError(f'Keyword arg is not a valid python '
                                  f'identifier: {key}')
        if keyword.iskeyword(key):
            raise InvalidArgError(f'Keyword arg cannot be a python keyword : '
                                  f'{key}')
        return Kwarg(key, value)
