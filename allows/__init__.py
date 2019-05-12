# -*- coding: utf-8 -*-

"""Top-level package for Allows."""

__all__ = ['allow', 'return_value', 'raise_exception', 'recieve_method', 'be_called_with']

__author__ = """Dave Anderson"""
__email__ = 'dave@dvndrsn.com'
__version__ = '0.1.0'

from .factory import *
from .exception import AllowsException
from .models import Allow, MockExtension, SideEffect
