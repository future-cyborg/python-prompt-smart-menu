# -*- coding: utf-8 -*-
"""Shared helper classes."""


class NestedDict:
    """A wrapper around a nested dict.

    Dict should be of the format that can be given to prompt_toolkit function:
        NestedCompleter.from_nested_dict(dict)
    """

    def __init__(self, nest: dict) -> None:
        """Initialize with dict."""
        self._nest = nest

    @property
    def nest(self) -> dict:
        """Nest property."""
        return self._nest


class Kwarg:
    """Represents a keyword argument as a key and value."""

    def __init__(self, key: str, value) -> None:  # noqa: ANN
        """Initialize with key and value."""
        self._key = key
        self._value = value

    def __repr__(self) -> str:
        """Print string representation."""
        return f'{self._key}={self._value}'

    def key(self) -> str:
        """Return key."""
        return self._key

    def value(self, val = None):  # noqa: ANN
        """Return or set value."""
        if val:
            self._value = val
        else:
            return self._value


class InvalidArgError(Exception):
    """Invalid argument. Wrapper around various built-in exceptions."""

    def __init__(self, ex: Exception) -> None:
        """Initialize with an exception, not a message."""
        self.args = [f'{type(ex).__name__}: {ex}']
