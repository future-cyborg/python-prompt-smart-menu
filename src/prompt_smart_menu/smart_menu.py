# -*- coding: utf-8 -*-
"""Build a command line menu declaratively."""

from collections import OrderedDict
from inspect import Parameter, signature
from typing import Callable, List, Tuple, Union

from prompt_smart_menu.helpers import InvalidArgError, Kwarg, NestedDict
from prompt_smart_menu.input_parser import InputParser


def is_list_of_strings(li: list) -> bool:
    """Return true if input is a list of strings."""
    return all(isinstance(elem, str) for elem in li)


def is_list_of_dicts(li: list) -> bool:
    """Return true if input is a list of dicts."""
    return all(isinstance(elem, dict) for elem in li)


def is_list_of_kwargs(li: list) -> bool:
    """Return true if input is a list of Kwargs."""
    return all(isinstance(elem, Kwarg) for elem in li)


class MenuNode:
    """The MenuNode class for PromptSmartMenu sub/commands.

    Don't use this class directly. Initialize with PromptSmartMenu.
    """

    def __init__(
        self, *,
        command: str,
        function: Callable = None,
        children: Union[List[dict], List[str], NestedDict] = None,
        parser: InputParser = InputParser(),
        validate_args: bool = False
    ) -> None:
        """Initialize by unpacking menu node dict.

        See documentation for full description of these fields. Including which
        are required.

        Args:
            command (str): The sub/command this menu node is for.
            function (Callable): The function to call, if this node is an
                end-point of the menu.
            children: The children of this node. See documentation.
            parser (InputParser): For command type casting. Defaults to parent
                node's parser.
            validate_args (bool): If true and has function, function arguments
                are checked for validity before calling function. Defaults to
                parent node's setting.
        """
        if (children and
            not isinstance(children, NestedDict) and
            not is_list_of_dicts(children) and
            not is_list_of_strings(children)
        ):  # noqa E124
            raise TypeError(f"Children of '{command}' are "
                            f"not an excepted type.")

        self._command = command
        self._function = function
        self._children = []
        self._parser = parser
        self._parse = parser.parse
        self._validate_args = validate_args

        if function and not isinstance(function, Callable):
            raise TypeError(f"{self.__class__.__name__} function must be"
                            f" callable. See '{command}'.")

        if function:
            if (children and
                not isinstance(children, NestedDict) and
                isinstance(children[0], dict)
            ):  # noqa E124
                raise TypeError(f"{self.__class__.__name__} cannot have a"
                                f" function and children nodes. "
                                f"See '{command}'.")
            self._children = children
        else:
            if (children is None or
                isinstance(children, NestedDict) or
                is_list_of_strings(children)
            ):  # noqa E124
                raise TypeError(f"{self.__class__.__name__} without a function"
                                f"require {self.__class__.__name__} as "
                                f"children nodes. See '{command}'.")

            child_commands = set()
            for child in children:
                if 'parser' not in child:
                    child['parser'] = self._parser
                if 'validate_args' not in child:
                    child['validate_args'] = self._validate_args
                self._children.append(MenuNode(**child))
                if child['command'] in child_commands:
                    raise TypeError(f"Multiple children node of '{command}' "
                                    f"share the same command: "
                                    f"{child['command']}")
                child_commands.add(child['command'])

    @staticmethod
    def _split_kwargs(args: list) -> Tuple[list, List[Kwarg]]:
        """Separate Kwargs from arguments."""
        try:
            kwarg_index = list(map(lambda a: isinstance(a, Kwarg), args)
                               ).index(True)
            kwargs = [*args[kwarg_index:]]
            if not is_list_of_kwargs(kwargs):
                raise SyntaxError(f'positional argument follows keyword '
                                  f'argument: {kwargs[0]}')
            return ([*args[:kwarg_index]], kwargs)
        except ValueError:
            return ([*args], [])

    def get_menu(self) -> dict:
        """Recursively build menu for auto-completion."""
        if not self._children:
            value = None
        elif isinstance(self._children, NestedDict):
            value = self._children.nest
        elif isinstance(self._children[0], str):
            value = set(self._children)
        elif isinstance(self._children[0], MenuNode):
            value = {}
            for child in self._children:
                value = {**child.get_menu(), **value}

        return {self._command: value}

    def process_arg(self, args_str: str):
        """Parse an argument from a command string and process appropriately.

        If this MenuNode has a function, the entire command string is parsed
        and sent to the function as arguments. Otherwise, a single argument is
        parsed and the remaining command string is sent to the appropriate
        child MenuNode, if it exists.

        Args:
            args_str (str): The command string to be parsed and processed.

        Raises:
            InvalidArgError: Raised in a few situations. If this MenuNode is
                not an end-point but was given no commands. If not an end-point
                and given a non-existent subcommand. If validate_args=True and
                arguments are invalid.
        """
        if self._function:
            args = self._parse(args_str, recurse=True)
            if(self._validate_args):
                self._validate_function_args(args)
            args, kwargs = self._split_kwargs(args)
            kwargs = {k.key(): k.value() for k in kwargs}
            return self._function(*args, **kwargs)
        elif args_str.strip() == '':
            e = ValueError('More arguments needed.')
            raise InvalidArgError(e)
        else:
            command, *args = self._parse(args_str)
            if args == []:
                args = ''
            else:
                args = args[0]

            for child in self._children:
                if child._command == command:
                    return child.process_arg(args)
            # This is if no valid child command is found
            e = ValueError('Subcommand not found: {command}')
            raise InvalidArgError(e)

    def _validate_function_args(self, args: list) -> None:
        """Validate a function's arguments before calling it."""
        args, kwargs = self._split_kwargs(args)

        sig = signature(self._function)
        parameters = OrderedDict()
        for k, v in sig.parameters.items():
            parameters[k] = [v, False]

        var_positional = False
        var_keyword = False

        remove_list = []
        # Remove *args and **kwargs from parameters and represent as bool
        for p in parameters:
            if parameters[p][0].kind == Parameter.VAR_POSITIONAL:
                var_positional = True
                remove_list.append(p)
            elif parameters[p][0].kind == Parameter.VAR_KEYWORD:
                var_keyword = True
                remove_list.append(p)
        for p in remove_list:
            parameters.pop(p)

        # Process kwargs
        extra_kwargs = {}
        for kwarg in kwargs:
            keyword = kwarg.key()
            if keyword in parameters:
                if parameters[keyword][1]:
                    e = SyntaxError(f'keyword argument repeated: {keyword}')
                    raise InvalidArgError(e)
                if parameters[keyword][0].kind == Parameter.POSITIONAL_ONLY:
                    e = TypeError(f"{self._function.__name__}() got some "
                                  f"positional-only arguments passed as "
                                  f"keyword arguments: '{keyword}'")
                    raise InvalidArgError(e)
                parameters[keyword][1] = True
            elif var_keyword:
                if keyword in extra_kwargs:
                    e = TypeError(f"{self._function.__name__}() got an "
                                  f"unexpected keyword argument '{keyword}'")
                    raise InvalidArgError(e)
                extra_kwargs[keyword] = keyword
            else:
                e = TypeError(f"{self._function.__name__}() got an "
                              f"unexpected keyword argument '{keyword}'")
                raise InvalidArgError(e)

        # Process args
        number_args = len(args)
        for p in parameters:
            if number_args <= 0:
                break
            if parameters[p][0].kind >= Parameter.KEYWORD_ONLY:
                break
            if parameters[p][1]:
                e = TypeError(f"{self._function.__name__}() got multiple "
                              f"values for argument 'p'")
                raise InvalidArgError(e)
            parameters[p][1] = True
            number_args -= 1

        # Extra positional arguments
        if number_args > 0 and not var_positional:
            e = TypeError(f"{self._function.__name__}() takes "
                          f"{len(parameters)} positional argument but "
                          f"{len(args)} were given")
            raise InvalidArgError(e)

        # Required params missing
        missing_positional = []
        missing_keyword_only = []
        for p in parameters:
            if (not parameters[p][1] and
                isinstance(parameters[p][0].default, type)
            ):  # noqa E124
                if parameters[p][0].kind < Parameter.KEYWORD_ONLY:
                    missing_positional.append(p)
                else:
                    missing_keyword_only.append(p)

        if missing_positional:
            e = TypeError(f"{self._function.__name__}() missing "
                          f"{len(missing_positional)} required arguments: "
                          f"{missing_positional}")
            raise InvalidArgError(e)

        if missing_keyword_only:
            e = TypeError(f"{self._function.__name__}() missing "
                          f"{len(missing_keyword_only)} required arguments: "
                          f"{missing_keyword_only}")
            raise InvalidArgError(e)

        # def _help(self):
        #     sig = signature(self._function)
        #     if len(sig.parameters) != len(args):
        #         pass


class PromptSmartMenu:
    """The main PromptSmartMenu class.

    Declare a menu's configuration as list of menu_node dicts. Initialize
    a PromptSmartMenu object with this configuration to generate a dict for
    auto-suggestion and to execute a command string against your menu.
    """

    def __init__(
        self,
        menu_config: List[dict],
        parser: InputParser = InputParser(),
        validate_args: bool = False
    ) -> None:
        """Initialize with menu configuration.

        See documentation for instructions on building the menu_config dict.

        Args:
            menu_config (List[dict]): List of menu nodes. See documentation.
            parser (InputParser): The input parser for the menu's root.
                Note: parser is inherited by child nodes, unless overwritten.
                Default: InputParser that treats all arguments as strings.
            validate_args: (bool): If true, arguments are validated before
                calling an end-point function. Default: False
        """
        if not is_list_of_dicts(menu_config):
            raise TypeError("menu_config takes a list of dictionaries.")
        if len(menu_config) == 0:
            raise ValueError("menu_config cannot be empty.")
        node = {'command': 'root',
                'function': None,
                'children': menu_config,
                'parser': parser,
                'validate_args': validate_args}
        self._root = MenuNode(**node)

    def nested_completer_dict(self) -> dict:
        """Return a dict for `prompt_toolkit.NestedCompleter`."""
        return self._root.get_menu()['root']

    def run(self, input_string: str):
        """Run a command string against with your menu."""
        return self._root.process_arg(input_string)
