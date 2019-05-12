# -*- coding: utf-8 -*-

from itertools import chain, repeat
from unittest.mock import call, Mock
from typing import Any, Callable

from .exception import AllowsException


class Allow:

    def __init__(self, mock_subject):
        self._mock_subject = mock_subject

    def to(self, mock_extension):
        return mock_extension._apply(self._mock_subject)


class MockExtension:

    def __init__(self, method_name=None, call_args=None, return_value=None, raised_exception=None, effect=None):
        self._method_name = method_name
        self._call_args = call_args
        self._effect = None
        self._set_effect_from_one_of(return_value, raised_exception, effect)

    def _set_effect_from_one_of(self, return_value, raised_exception, effect):
        if sum(bool(value) for value in [return_value, raised_exception, effect]) > 1:
            raise AllowsException('Only one effect can be provided')
        if return_value:
            self._set_return_value(return_value)
        if raised_exception:
            self._set_raised_exception(raised_exception)
        if effect:
            self._set_effect(effect)

    def _set_method_name(self, method_name):
        if self._method_name:
            raise AllowsException('Cannot set mutliple method names in one effect')
        self._method_name = method_name
        return self

    def on_method(self, method_name):
        return self._set_method_name(method_name)

    def _set_call_args(self, *args, **kwargs):
        if self._call_args:
            raise AllowsException('Cannot set multiple call args in one effect')
        self._call_args = call(*args, **kwargs)
        return self

    def called_with(self, *args, **kwargs):
        return self._set_call_args(*args, **kwargs)

    def when_called_with(self, *args, **kwargs):
        return self._set_call_args(*args, **kwargs)

    def _set_return_value(self, *return_values: Any):
        return_value_iterator = iter(chain(return_values, repeat(return_values[-1])))
        def return_next(*args, **kwargs):
            return next(return_value_iterator)

        effect = return_next
        return self._set_effect(effect)

    def and_return(self, *return_value):
        return self._set_return_value(*return_value)

    def and_return_value(self, *return_value):
        return self._set_return_value(*return_value)

    def _set_raised_exception(self, raised_exception):
        def raise_(exception):
            raise exception

        effect = lambda *args, **kwargs: raise_(raised_exception)
        return self._set_effect(effect)

    def and_raise(self, raised_exception):
        return self._set_raised_exception(raised_exception)

    def and_raise_exception(self, raised_exception):
        return self._set_raised_exception(raised_exception)

    def _set_effect(self, effect):
        if self._effect:
            raise AllowsException('Cannot set multiple effects')

        self._effect = lambda *args, **kwargs: effect(*args, **kwargs)
        return self

    def with_effect(self, effect: Callable):
        return self._set_effect(effect)

    def _apply(self, mock_subject):
        mock_method = self._get_method_from_mock(mock_subject)
        mock_method.side_effect = SideEffect.from_base(mock_method.side_effect, call_args=self._call_args, effect=self._effect)
        return mock_subject

    def _get_method_from_mock(self, mock_subject):
        if not self._method_name:
            return mock_subject
        method_path = self._method_name.split('.')
        for method in method_path:
            mock_subject = getattr(mock_subject, method)
        return mock_subject


class SideEffect:

    def __init__(self, call_args=None, effect=None):
        if not call_args:
            call_args = call()
        if not effect:
            effect = lambda: None
        self._calls = [call_args]
        self._effects = [effect]

    def __call__(self, *args, **kwargs):
        call_args = call(*args, **kwargs)
        effect = self._effect_lookup(call_args)
        return effect(*args, **kwargs)

    def _effect_lookup(self, call_args):
        call_index = self._calls.index(call_args)
        return self._effects[call_index]

    def merge(self, other: 'SideEffect'):
        if isinstance(other, self.__class__):
            self._calls.extend(other._calls)
            self._effects.extend(other._effects)
        raise AllowsException('Cannot merge effects that are not SideEffect')

    @classmethod
    def from_base(cls, base_side_effect=None, call_args=None, effect=None):
        if isinstance(base_side_effect, cls):
            return base_side_effect.merge(cls(call_args=call_args, effect=effect))
        elif not base_side_effect:
            return cls(call_args=call_args, effect=effect)
        raise AllowsException('Cannot extend side effect that is not from this base')
