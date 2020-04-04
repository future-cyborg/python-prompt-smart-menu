# -*- coding: utf-8 -*-

from prompt_smart_menu import PromptSmartMenu
from prompt_smart_menu.helpers import InvalidArgError
from prompt_smart_menu.input_parser import InputParser, KwargCast, NumberCast

import pytest


def dummy(*args, **kwargs):
    return (args, kwargs)


def dummy_wrapper(s: str):
    return lambda *args, **kwargs: dummy(s, *args, **kwargs)


@pytest.fixture
def menu_fixture():
    menu_config = [
        {
            'command': 'tree',
            'function': None,
            'children': [{
                'command': 'leaf',
                'function': dummy_wrapper('leaf'),
                'children': None
            }]
        },
        {
            'command': 'root',
            'function': dummy_wrapper('root'),
        }
    ]
    return PromptSmartMenu(menu_config)


class TestPromptSmartMenu:

    def test_empty_menu_config_raises(self):
        menu = []
        with pytest.raises(ValueError):
            PromptSmartMenu(menu)

    def test_bad_type_menu_config_raises(self):
        menu = ['test']
        with pytest.raises(TypeError):
            PromptSmartMenu(menu)

    def test_nested_completer_dict_simple(self):
        expected = {'test': None}
        menu = [{'command': 'test', 'function': dummy}]

        psm = PromptSmartMenu(menu)
        assert psm.nested_completer_dict() == expected

    def test_nested_completer_dict_children(self):
        expected = {'test': None, 'prompt': {'smart', 'menu'}}
        menu = [{'command': 'test', 'function': dummy},
                {'command': 'prompt', 'function': dummy,
                 'children': ['smart', 'menu']}]

        psm = PromptSmartMenu(menu)
        assert psm.nested_completer_dict() == expected

    def test_nested_completer_dict_child_nodes(self):
        expected = {'test': None, 'prompt': {'smart': None, 'menu': None}}

        child_1 = {'command': 'smart', 'function': dummy}
        child_2 = {'command': 'menu', 'function': dummy}
        menu = [{'command': 'test', 'function': dummy},
                {'command': 'prompt', 'children': [child_1, child_2]}]

        psm = PromptSmartMenu(menu)
        assert psm.nested_completer_dict() == expected

    def test_run_root(self, menu_fixture):
        assert menu_fixture.run('root') == (('root',), {})
        expected = (('root', 'prompt', 'smart'), {})
        assert menu_fixture.run('root prompt smart') == expected

    def test_run_tree_raises(self, menu_fixture):
        with pytest.raises(InvalidArgError):
            menu_fixture.run('tree')

    def test_run_tree_leaf(self, menu_fixture):
        assert menu_fixture.run('tree leaf') == (('leaf',), {})
        assert menu_fixture.run('tree leaf prompt') == (('leaf', 'prompt'), {})


def dummy_no_args():
    pass


@pytest.fixture
def complex_menu_fixture():
    menu_config = [
        {
            'command': 'tree',
            'function': None,
            'children': [
                {
                    'command': 'dummy',
                    'function': dummy,
                },
                {
                    'command': 'all_str',
                    'function': dummy,
                    'parser': InputParser()
                },
                {
                    'command': 'no_validate',
                    'function': dummy_no_args,
                    'validate_args': False
                }
            ]
        },
        {
            'command': 'root',
            'function': lambda: 42,
        }
    ]
    return PromptSmartMenu(menu_config,
                           parser=InputParser(KwargCast, NumberCast),
                           validate_args=True)


class TestComplexMenu:
    def test_root(self, complex_menu_fixture):
        result = complex_menu_fixture.run('root')
        assert result == 42

    @pytest.mark.parametrize('item,item_type', [('9', int), ('9.0', float)])
    def test_parser_inherits_cast_number(
        self,
        complex_menu_fixture,
        item,
        item_type
    ):
        result = complex_menu_fixture.run(f'tree dummy {item}')
        assert isinstance(result[0][0], item_type)
        assert result[0][0] == item_type(item)

    @pytest.mark.parametrize('item', ['--key=val'])
    def test_parser_inherits_cast_kwarg(self, complex_menu_fixture, item):
        result = complex_menu_fixture.run(f'tree dummy {item}')
        print(f'result: {result}')
        assert isinstance(result[1], dict)

    @pytest.mark.parametrize('item', ['2', '--key=val'])
    def test_parser_overwrites(self, complex_menu_fixture, item):
        result = complex_menu_fixture.run(f'tree all_str {item}')
        assert isinstance(result[0][0], str)

    def test_validate_args_overwrites(self, complex_menu_fixture):
        with pytest.raises(TypeError):
            complex_menu_fixture.run(f'tree no_validate error')
