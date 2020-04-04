.. _command_parsing:

Command parsing
===============

For parsing a command string into arguments, the default parser follows these rules:

- All whitespace is equivalent and separates arguments.
- Quotes can be used encapsulate whitespace. ``'``, ``"``, ````` can all be used. They all function 
  the same way, only differing in which of the others can be encapsulated. There is no logic to 
  use a backslash to include a quote literal.
- Once a command has been parsed, a type cast is attempted. The default treats everything like a string.
- Only one command is extracted at a time. The remaining part of the string is then sent to the 
  appropriate child node. This enables having different type casting for different subcommands.

Type casting
------------

The default behavior is to treat everything like a string. Additional type casters can be added 
to an InputParser during initialization.

.. code-block:: python

    InputParser(KwargCast, NumberCast)

Each cast will be done sequentially on a given argument.

NumberCast
^^^^^^^^^^

A simple cast for ints and floats following the regular python logic.

+----------+-------+
| Argument | Type  |
+==========+=======+
| 2        | int   |
+----------+-------+
| 2.0      | float |
+----------+-------+
| "2"      | str   |
+----------+-------+

Keyword arguments
-----------------

Keyword arguments are supported with the KwargCast class. This enables passing arguments to a
function as a keyword argument. They take the long option format. ``--keyword=value``

When using keyword arguments, the normal python logic for ordering arguments is used. That is, keyword 
arguments must all come after positional arguments.

Other cast classes should be able to cast a keyword value. This makes the order of declaring casters
while initializing ``InputParser()`` relevant. If you want the value of ``--keyword=2`` to be 
interpreted as a number, then ``KwargCast`` should be inserted before ``NumberCast``.


Customer Caster
---------------

To make a custom cast class, all that is needed is the ``type_cast()`` function. This function should 
return the input if a cast is not possible. Here is a template class, with logic for casting a keyword 
argument's value.

.. code-block:: python

    class TemplateCast:
        @classmethod
        def type_cast(cls, item):
            if isinstance(item, Kwarg):
                item.value(cls._type_cast(item.value()))
            else:
                item = cls._type_cast(item)
            return item

        @staticmethod
        def _type_cast(item: str):
            if :    # Logic for interpreting string
                item =    # Logic for casting string
            return item


Custom Parser
-------------

A custom parser with different rules for handling whitespace could be built and used in place of 
:py:class:`InputParser`.