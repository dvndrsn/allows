from typing import Any, Callable
from unittest.mock import Mock, call

from .models import Allow, MockExtension


def allow(mock_subject: Mock) -> 'Allow':
    return Allow(mock_subject)


def return_value(return_value: Any) -> 'MockExtension':
    return MockExtension()._set_return_value(return_value)


def return_(value: Any) -> 'MockExtension':
    return return_value(value)


def raise_exception(raised_exception: Exception) -> 'MockExtension':
    return MockExtension()._set_raised_exception(raise_exception)


def raise_(exception: Exception) -> 'MockExtension':
    return raise_exception(exception)


def recieve(method_name):
    return MockExtension()._set_method_name(method_name)


def recieve_method(name):
    return recieve(name)


def be_called_with(*args, **kwargs):
    return MockExtension()._set_call_args(*args, **kwargs)
