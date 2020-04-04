# -*- coding: utf-8 -*-

from prompt_smart_menu.helpers import InvalidArgError, Kwarg
from prompt_smart_menu.input_parser import InputParser, KwargCast, NumberCast

import pytest


class TestInputParser:
    ip = InputParser()

    def test_parse_single(self):
        expected = ['prompt']
        assert self.ip.parse('  prompt') == expected
        assert self.ip.parse('prompt') == expected
        assert self.ip.parse('\t prompt') == expected

    def test_parse_multiple(self):
        expected = ['prompt', 'smart']
        assert self.ip.parse('prompt smart') == expected
        assert self.ip.parse('prompt \t\nsmart') == expected

        expected = ['prompt', 'smart menu']
        assert self.ip.parse('prompt smart menu') == expected
        expected = ['prompt', 'smart  menu']
        assert self.ip.parse('prompt smart  menu') == expected

    def test_parse_trailing_whitespace(self):
        expected = ['prompt']
        assert self.ip.parse('prompt ') == expected
        assert self.ip.parse('prompt \t') == expected

    def test_parse_blank(self):
        expected = []
        assert self.ip.parse('') == expected
        assert self.ip.parse('  ') == expected

    def test_parse_quotes(self):
        expected = ['prompt smart']
        assert self.ip.parse('"prompt smart"') == expected
        assert self.ip.parse("'prompt smart'") == expected
        assert self.ip.parse('`prompt smart`') == expected
        assert self.ip.parse("'prompt smart'  \t") == expected

        expected = ['prompt', 'smart']
        assert self.ip.parse("'prompt' smart") == expected
        assert self.ip.parse('"prompt" smart') == expected
        assert self.ip.parse('`prompt` smart') == expected

        expected = ['prompt', '"smart"']
        assert self.ip.parse('prompt "smart"') == expected

        expected = ['prompt', "'smart'"]
        assert self.ip.parse("prompt 'smart'") == expected

        expected = ['prompt', '`smart`']
        assert self.ip.parse('prompt `smart`') == expected

    def test_parse_quotes_multiple(self):
        expected = ['prompt', '"smart_menu"']
        assert self.ip.parse('"prompt""smart_menu"') == expected
        assert self.ip.parse('"prompt"  \t"smart_menu"') == expected

    def test_parse_quotes_empty(self):
        expected = ['']
        assert self.ip.parse("''") == expected
        assert self.ip.parse('""') == expected
        assert self.ip.parse('``') == expected

        expected = ['', 'prompt']
        assert self.ip.parse("'' prompt") == expected
        assert self.ip.parse('"" prompt') == expected
        assert self.ip.parse('`` prompt') == expected

    def test_parse_quote_raises(self):
        with pytest.raises(ValueError):
            self.ip.parse('"foo')

        with pytest.raises(ValueError):
            self.ip.parse("'foo")

        with pytest.raises(ValueError):
            self.ip.parse('`foo')

    def test_parse_recurse_quotes_empty(self):
        expected = ['prompt', '']
        assert self.ip.parse('prompt ""', recurse=True) == expected
        assert self.ip.parse("prompt ''", recurse=True) == expected
        assert self.ip.parse('prompt ``', recurse=True) == expected

    def test_parse_recurse(self):
        expected = ['prompt', 'smart', 'menu']
        assert self.ip.parse('prompt smart menu', recurse=True) == expected
        assert self.ip.parse(' prompt smart menu  ', recurse=True) == expected


class TestNumberCast:
    ip = InputParser(NumberCast)

    @pytest.mark.parametrize('i', ['0', '2', '-2'])
    def test_parse_int(self, i):
        assert self.ip.parse(i) == [int(i)]
        assert isinstance(self.ip.parse(i)[0], int)

    @pytest.mark.parametrize('f', ['0.0', '-1.2', '012.345'])
    def test_parse_float(self, f):
        assert self.ip.parse(f) == [float(f)]
        assert isinstance(self.ip.parse(f)[0], float)

    @pytest.mark.parametrize('s', ['"2"', "'2'", '`2`'])
    def test_parse_quotes(self, s):
        assert self.ip.parse(s) == ['2']
        assert self.ip.parse(s) == ['2']
        assert self.ip.parse(s) == ['2']


class TestNumberKwargCast:
    ip = InputParser(KwargCast, NumberCast)

    def test_kwarg_value(self):
        result = self.ip.parse('--key=2')
        assert isinstance(result[0], Kwarg)
        assert result[0].value() == 2


class TestKwargCast:
    ip = InputParser(KwargCast)

    @staticmethod
    def kwarg_str(key, value):
        return f'--{ key }={ value }'

    @pytest.mark.parametrize('key,value', [('K', ''),
                                           ('k', 'val'),
                                           ('_Foo9', '$#$*%'),
                                           ])
    def test_success(self, key, value):
        arg = self.kwarg_str(key, value)

        kwarg = self.ip.parse(arg)[0]
        assert kwarg.key() == key
        assert kwarg.value() == value

    @pytest.mark.parametrize('string', ['-k=v',
                                        '---k=v',
                                        '--=v',
                                        'k#',
                                        'k@',
                                        ])
    def test_inert(self, string):
        assert self.ip.parse(string)[0] == string

    @pytest.mark.parametrize('key', ['9',
                                     'global',
                                     'for',
                                     ])
    def test_bad_identifier_raises(self, key):
        arg = self.kwarg_str(key, '')

        with pytest.raises(InvalidArgError):
            self.ip.parse(arg)


class TestMultiCast:

    kn_inputs = [
        (InputParser(KwargCast, NumberCast), '--key=val', Kwarg),
        (InputParser(KwargCast, NumberCast), '--key=val', Kwarg),
        (InputParser(KwargCast, NumberCast), '3.14', float),
        (InputParser(KwargCast, NumberCast), '3.14', float),
    ]

    @pytest.mark.parametrize('ip,arg,arg_type', kn_inputs)
    def test_kwarg_number(self, ip, arg, arg_type):
        ip = InputParser(KwargCast, NumberCast)

        assert isinstance(ip.parse(arg)[0], arg_type)
