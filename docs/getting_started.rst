.. _getting_started:

Getting started
===============

Installation
------------

::

    pip install prompt_smart_menu


A simple menu
-------------

This example menu will accept the following commands, each leading to a separate function 
that takes no arguments.

- ``exit``
- ``show version``
- ``show clock``

First, declare the menu structure.

.. code:: python

    from prompt_smart_menu import PromptSmartMenu

    menu_config = [
        {
            'command': 'exit',
            'function': exit,
        },
        {
            'command': 'show',
            'children': [
                {
                    'command': 'version',
                    'function': show_version,
                },
                {
                    'command': 'clock',
                    'function': show_clock
                }
            ]
        }
    ]

Now we can create the menu object, and pass it a command via ``run()``.

.. code:: python

    smart_menu = PromptSmartMenu(menu_config)
    command = input('Enter command >')
    smart_menu.run(command)


Auto-complete integration
-------------------------

PromptSmartMenu can easily create configuration for use with prompt_toolkit's
`NestedCompleter <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html#nested-completion>`__

.. code-block:: python

    from prompt_toolkit.completion import NestedCompleter

    nested_dict = smart_menu.nested_completer_dict()
    completer = NextedCompleter.from_nested_dict(nested_dict)


Learning `prompt_smart_menu`
----------------------------

In order to learn and understand `prompt_toolkit`, it is best to go through the
all sections in the order below. Also don't forget to have a look at all the
examples `examples
<https://github.com/jonathanslenders/python-prompt-toolkit/tree/master/examples>`_
in the repository.

- First, :ref:`learn how to print text <printing_text>`. This is important,
  because it covers how to use "formatted text", which is something you'll use
  whenever you want to use colors anywhere.

- Secondly, go through the :ref:`asking for input <asking_for_input>` section.
  This is useful for almost any use case, even for full screen applications.
  It covers autocompletions, syntax highlighting, key bindings, and so on.

- Then, learn about :ref:`dialogs`, which is easy and fun.

- Finally, learn about :ref:`full screen applications
  <full_screen_applications>` and read through :ref:`the advanced topics
  <advanced_topics>`.
