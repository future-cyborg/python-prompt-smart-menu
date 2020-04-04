.. _menu_configuration:

Building a Menu
===============

A menu is constructed as a list of menu_node dicts. Each menu node is equivalent to a command 
(or subcommand).

menu_node structure
-------------------

Each menu_node is a dict that takes the following keys:

+---------------+--------------------------------------------------------------------+
| Key           | Value                                                              |
+===============+====================================================================+
| command       | str: The argument command.                                         |
+---------------+--------------------------------------------------------------------+
| function      | function: The function to execute.                                 |
+---------------+--------------------------------------------------------------------+
| children      | list or dict: Subcommand or auto-completion children. See below.   |
+---------------+--------------------------------------------------------------------+
| parser        | InputParer: For parsing command string and type casting arguments. |
+---------------+--------------------------------------------------------------------+
| validate_args | bool: Validate arguments before running function.                  |
+---------------+--------------------------------------------------------------------+


Each menu_node requires the ``command`` key and either ``function`` or ``children``.

.. note::

    The ``parser`` and ``validate_args`` values are inherited from a menu_node's parent 
    unless explicitly defined.


menu_node children
------------------

A menu_node has a few options for ``children``.

1. A list of menu_nodes. For adding subcommands. ``function`` **must be None** with this option.

.. code-block:: python

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

2. A list of strings. This is strictly for auto-completion. ``function`` **must be declared**
   with this option.

.. code-block:: python

    {
        'command': 'show',
        'function': show
        'children': ['comments', 'posts']
    }

3. A NestedDict wrapped dictionary of the same format used with
   :py:class:`prompt_toolkit:prompt_toolkit.completion.NestedCompleter`.
   This is strictly for auto-completion. ``function`` **must be declared** with this option.

.. code-block:: python

    from prompt_smart_menu import NestedDict

    {
        'command': 'show',
        'function': show
        'children': NestedDict(
            {
                'version': None,
                'interfaces': None,
                'clock': None,
                'ip': {'interface': {'brief'}}
            }
        )
    }


PromptSmartMenu
---------------

Once a menu's configuration has been declared. Simply initialize a PromptSmartMenu with it.
The ``parser`` and ``validate_args`` options can also be declared here; in most situations 
this makes the most sense.

.. code-block:: python

    from prompt_smart_menu import PromptSmartMenu
    from prompt_smart_menu.input_parser import InputParser, KwargCast, NumberCast

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

    psm = PromptSmartMenu(
            menu_config,
            parser=InputParser(KwargCast, NumberCast),
            validate_args=True)
