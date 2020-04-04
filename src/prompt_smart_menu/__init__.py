# -*- coding: utf-8 -*-
"""
prompt_smart_menu
=================

Description: prompt_smart_menu is a library for building command line menus for
             terminal applications in Python. It allows you to create a
             multi-tiered argument parsing menu for executing different
             subcommands of a command line application.

See documentation for usage.
"""
from pkg_resources import DistributionNotFound, get_distribution

try:
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

from .helpers import NestedDict
from .smart_menu import PromptSmartMenu


__author__ = "Yesha"
__copyright__ = "Copyright (c) Yesha, 2020"
__license__ = "mit"


__all__ = ['NestedDict', 'PromptSmartMenu']
