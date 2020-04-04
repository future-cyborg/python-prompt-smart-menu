.. _argument_validation:

Validating arguments
====================

Argument validation can be turned on to catch errors due to passing invalid arguments to a 
function. When activated a ``InvalidArgError`` is raised in place of certain default python 
exceptions that pertain to a function's arguments. The types of errors this will catch include:

- SyntaxError: keyword argument repeated:
- TypeError: function() got an unexpected keyword argument
- TypeError: function() got multiple values for argument ''
- TypeError: function() takes # positional arguments but # were given.
- TypeError: function() missing # required arguments: 

These are identified through python inspection, not by running the function. Since python is 
dynamically typed, this will not catch type errors associated with type.
