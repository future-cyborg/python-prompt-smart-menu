=======================
Python Prompt SmartMenu
=======================

`prompt_smart_menu` is a library for building command line menus for terminal applications 
in Python. It allows you to create a multi-tiered argument parsing menu for executing
different subcommands of a command line application.

Read the `documentation on readthedocs
<http://python-prompt-smart-menu.readthedocs.io/en/latest/>`_.


Description
===========

This library is designed around parsing a command string, not command line arguments. That is,
it is intended to be used inside a python application using an ``input()`` type interface.

For command line arguments passed to the python script, a library such as argparse would be 
better suited. Though this library could be used for such purpose.

Though not required, this library was designed to augment the 
`auto-completion <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html#nested-completion>`__ 
feature of `Python Prompt Toolkit`_. The `prompt_toolkit` library is very powerful, check it out!


Features
========

- **Declarative interface** (That's why I built this :] )
- Integration with `prompt_toolkit auto-completion <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html#nested-completion>`__
- Support for python keyword arguments.
- Different parsers for type casting arguments (e.g. numbers).
- Ability to build custom argument parser.
- Argument validation for endpoint functions.
- Flexibility to mix options (e.g. parsers) for different subcommands.
- No dependencies, though `prompt_toolkit` highly recommended.


Installation
============

::

    pip install prompt_smart_menu


Getting started
===============

See documentation on `readthedocs <http://python-prompt-smart-menu.readthedocs.io/en/latest/>`_.


.. _Python Prompt Toolkit: https://python-prompt-toolkit.readthedocs.io/en/stable/index.html
