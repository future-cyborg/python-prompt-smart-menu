# -*- coding: utf-8 -*-

import itertools

from prompt_smart_menu.helpers import InvalidArgError, Kwarg, NestedDict
from prompt_smart_menu.smart_menu import MenuNode

import pytest


def dummy(*args, **kwargs):
    pass


class TestMenuNode:
    _nest = {'prompt': {'toolkit', 'menu'}, 'exit': None}

    def test_init_children_mismatch_type(self):
        mismatch_1 = ['string', {'k': 'v'}]
        mismatch_2 = [NestedDict, 'string']
        node_1 = {'command': 'test', 'function': None, 'children': mismatch_1}
        node_2 = {'command': 'test', 'function': None, 'children': mismatch_2}

        with pytest.raises(TypeError):
            MenuNode(**node_1)
        with pytest.raises(TypeError):
            MenuNode(**node_2)

    def test_init_missing_kwargs(self):
        no_command = {'function': None, 'children': [1]}
        no_child = {'command': 'test', 'function': dummy}
        no_func = {'command': 'test', 'children': [no_child]}

        with pytest.raises(TypeError):
            MenuNode(**no_command)
        MenuNode(**no_func)
        MenuNode(**no_child)

    def test_init_children_none_no_function_raises(self):
        node = {'command': 'test', 'function': None, 'children': None}
        with pytest.raises(TypeError):
            MenuNode(**node)

    def test_init_children_none_with_function_successful(self):
        node = {'command': 'test', 'function': dummy, 'children': None}
        MenuNode(**node)

    def test_init_children_empty_list_no_function_raises(self):
        node = {'command': 'test', 'function': None, 'children': []}
        with pytest.raises(TypeError):
            MenuNode(**node)

    def test_init_children_empty_list_with_function_successful(self):
        node = {'command': 'test', 'function': dummy, 'children': []}
        MenuNode(**node)

    def test_init_children_nested_dict_no_function_raises(self):
        nested_dict = NestedDict(self._nest)
        node = {'command': 'test', 'function': None, 'children': nested_dict}
        with pytest.raises(TypeError):
            MenuNode(**node)

    def test_init_children_nested_dict_with_function_successful(self):
        nested_dict = NestedDict(self._nest)
        node = {'command': 'test', 'function': dummy, 'children': nested_dict}
        MenuNode(**node)

    def test_init_children_list_string_no_function_raises(self):
        node = {'command': 'test', 'function': None,
                'children': ['prompt', 'menu']}
        with pytest.raises(TypeError):
            MenuNode(**node)

    def test_init_children_list_string_with_function_successful(self):
        node = {'command': 'test', 'function': dummy,
                'children': ['prompt', 'menu']}
        MenuNode(**node)

    def test_init_children_list_dict_no_function_successful(self):
        child = {'command': 'bob', 'function': dummy, 'children': None}
        node = {'command': 'test', 'function': None, 'children': [child]}
        MenuNode(**node)

    def test_init_children_list_dict_with_function_raises(self):
        child = {'command': 'bob', 'function': dummy, 'children': None}
        node = {'command': 'test', 'function': dummy, 'children': [child]}
        with pytest.raises(TypeError):
            MenuNode(**node)

    def test_init_duplicate_child_commands(self):
        child_1 = {'command': 'bob', 'function': dummy, 'children': None}
        child_2 = child_1
        node = {'command': 'test', 'function': None,
                'children': [child_1, child_2]}

        with pytest.raises(TypeError):
            MenuNode(**node)

    def test_get_menu_children_none(self):
        expected = {'test': None}

        node_1 = {'command': 'test', 'function': dummy, 'children': None}
        node_2 = {'command': 'test', 'function': dummy, 'children': []}

        assert MenuNode(**node_1).get_menu() == expected
        assert MenuNode(**node_2).get_menu() == expected

    def test_get_menu_children_nested_dict(self):
        expected = {'test': self._nest}

        nested_dict = NestedDict(self._nest)
        node = {'command': 'test', 'function': dummy, 'children': nested_dict}

        assert MenuNode(**node).get_menu() == expected

    def test_get_menu_children_list_strings(self):
        expected = {'test': {'prompt', 'menu'}}
        node = {'command': 'test', 'function': dummy,
                'children': ['prompt', 'menu']}

        assert MenuNode(**node).get_menu() == expected

    def test_get_menu_children_list_nodes(self):
        expected = {'test': {'prompt': {'toolkit', 'menu'}, 'exit': None}}
        children = [{'command': 'prompt', 'function': dummy,
                     'children': ['toolkit', 'menu']},
                    {'command': 'exit', 'function': dummy, 'children': None}]
        node = {'command': 'test', 'function': None, 'children': children}

        assert MenuNode(**node).get_menu() == expected


class TestMenuNodeProcessArg:

    def test_no_function_no_args(self):
        child = {'command': 'child', 'function': dummy}
        node = {'command': 'test', 'children': [child]}
        menu_node = MenuNode(**node)

        with pytest.raises(InvalidArgError):
            menu_node.process_arg('')

    def test_no_function_no_matching_child(self):
        child = {'command': 'child', 'function': dummy}
        node = {'command': 'test', 'children': [child]}
        menu_node = MenuNode(**node)

        with pytest.raises(InvalidArgError):
            menu_node.process_arg('prompt')

    def test_calls_function(self):
        node = {'command': 'test', 'function': lambda: 42}
        menu_node = MenuNode(**node)

        assert menu_node.process_arg('') == 42

    def test_calls_child_function(self):
        child = {'command': 'child', 'function': lambda: 42}
        node = {'command': 'test', 'children': [child]}
        menu_node = MenuNode(**node)

        assert menu_node.process_arg('child') == 42


class TestMenuNodeSplitKwargs:

    def test_empty(self):
        expected = ([], [])
        assert MenuNode._split_kwargs([]) == expected

    def test_only_args(self):
        args = [1, 'test']
        expected = (args, [])
        assert MenuNode._split_kwargs(args) == expected

    def test_only_kwargs(self):
        kwargs = [Kwarg('test', 1), Kwarg('test', 2)]
        expected = ([], kwargs)
        assert MenuNode._split_kwargs(kwargs) == expected

    def test_args_first(self):
        args = [1, 'test']
        kwargs = [Kwarg('test', 1), Kwarg('test', 2)]
        expected = (args, kwargs)
        assert MenuNode._split_kwargs([*args, *kwargs]) == expected

    def test_kwargs_first(self):
        args = [1, 'test']
        kwargs = [Kwarg('test', 1), Kwarg('test', 2)]

        with pytest.raises(SyntaxError):
            MenuNode._split_kwargs([*kwargs, *args])

    def test_mixed(self):
        li = [1, Kwarg('test', 1), 'test']
        with pytest.raises(SyntaxError):
            MenuNode._split_kwargs(li)


def no_args_func():
    pass

# # Can only test with python 3.8
# def positional_only(a, /):
#     pass


def positional_or_keyword(b, c='c'):
    pass


def var_positional(*d):
    pass


def keyword_only(*, e, f='f'):
    pass


def var_keyword(**g):
    pass


# def validate_dummy(a, /, b, c='c', *d, e, f='f', **g):
#     pass


def pack_args(letters: str, number_args: int):
    args = [a for a in range(number_args)]
    for k in letters:
        args.append(Kwarg(k, k))
    return args


def get_arg_combos(
    letters: str,
    number_args_min: int = 0,
    number_args_max: int = 1
):
    results = []
    combinations = ['']
    for r in range(1, len(letters) + 1):
        for combo in itertools.combinations(letters, r):
            combinations.append(''.join(combo))
    for combo in combinations:
        for number_args in range(number_args_min, number_args_max):
            results.append((combo, number_args))
    return results


class TestValidateFunctionArgs:
    def template_test(self, func, letters, number_args):
        args_packed = pack_args(letters, number_args)
        args, kwarg_objects = MenuNode._split_kwargs(args_packed)

        kwargs = {kw.key(): kw.value() for kw in kwarg_objects}
        print(kwargs)

        menu = {'command': 'test', 'function': func}
        mn = MenuNode(**menu)

        try:
            mn._function(*args, **kwargs)
        except TypeError:
            with pytest.raises(InvalidArgError):
                mn._validate_function_args(args_packed)
        else:
            # assert anything here?
            mn._validate_function_args(args_packed)

    # @pytest.mark.parametrize('letters,number_args',
    #                          get_arg_combos('bcefg', 1,5))
    # def test_validate_function_args(self, letters, number_args):
    #     self.template_test(validate_dummy, letters, number_args)

    @pytest.mark.parametrize('letters,number_args', get_arg_combos('g', 0, 2))
    def test_no_args_func(self, letters, number_args):
        self.template_test(no_args_func, letters, number_args)

    # # Can only test with python 3.8
    # @pytest.mark.parametrize('letters,number_args', get_arg_combos('', 0, 3))
    # def test_positional_only(self, letters, number_args):
    #     self.template_test(positional_only, letters, number_args)

    @pytest.mark.parametrize('letters,number_args', get_arg_combos('bc', 0, 2))
    def test_positional_or_keyword(self, letters, number_args):
        self.template_test(positional_or_keyword, letters, number_args)

    @pytest.mark.parametrize('letters,number_args', get_arg_combos('bc', 0, 2))
    def test_var_positional(self, letters, number_args):
        self.template_test(var_positional, letters, number_args)

    @pytest.mark.parametrize('letters,number_args', get_arg_combos('ef', 0, 1))
    def test_keyword_only(self, letters, number_args):
        self.template_test(keyword_only, letters, number_args)

    @pytest.mark.parametrize('letters,number_args', get_arg_combos('g', 0, 1))
    def test_var_keyword(self, letters, number_args):
        self.template_test(var_keyword, letters, number_args)

    @pytest.mark.parametrize('func,exception',
                             [(var_keyword, InvalidArgError),
                              (keyword_only, InvalidArgError)])
    def test_duplicate_keyword(self, func, exception):
        menu = {'command': 'test', 'function': func}
        mn = MenuNode(**menu)
        kwargs = [Kwarg('e', 'prompt'), Kwarg('e', 'prompt')]

        with pytest.raises(exception):
            mn._validate_function_args(kwargs)
