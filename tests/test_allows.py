#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `allows` package."""

from unittest.mock import Mock

import pytest

from allows import allow, be_called_with, raise_exception, recieve_method, return_value, AllowsException


class TestGrammarAllowsReturningAValue:

    def test_none_is_returned_by_default(self):
        mock_subject = Mock()

        allow(mock_subject).to(recieve_method('foo'))

        assert mock_subject.foo() is None

    def test_returns_the_specified_return_value(self):
        mock_subject = Mock()

        allow(mock_subject).to(recieve_method('foo').and_return_value('bar'))

        assert mock_subject.foo() == 'bar'

    def test_returns_the_specified_values_in_order_then_keeps_returning_the_last_value(self):
        mock_subject = Mock()

        allow(mock_subject).to(recieve_method('foo').and_return(1, 2, 3))

        assert mock_subject.foo() == 1
        assert mock_subject.foo() == 2
        assert mock_subject.foo() == 3
        assert mock_subject.foo() == 3
        assert mock_subject.foo() == 3

    def test_setting_method_twice_raises_error(self):
        mock_subject = Mock()

        with pytest.raises(AllowsException):
            allow(mock_subject).to(recieve_method('foo').on_method('foo'))

    def test_setting_return_value_twice_raises_error(self):
        mock_subject = Mock()

        with pytest.raises(AllowsException):
            allow(mock_subject).to(recieve_method('foo').and_return_value('bar').and_return_value('bar2'))


class TestAllowsGrammar:

    def test_return_value(self):
        mock_subject = Mock()

        allow(mock_subject).to(recieve_method('process').called_with('stuff', thing='hi').and_return_value('things'))

        mocked_return_value = mock_subject.process('stuff', thing='hi')
        assert mocked_return_value == 'things'

    def test_raises_exception(self):
        mock_subject = Mock()

        allow(mock_subject).to(recieve_method('process').called_with('badstuff', thing='yo').and_raise(ValueError('Bad Stuff')))

        with pytest.raises(ValueError):
            mock_subject.process('badstuff', thing='yo')

    def test_with_effect(self):
        mock_subject = Mock()

        allow(mock_subject).to(recieve_method('process').called_with('stuff', thing='hey').with_effect(lambda *args, **kwargs: 2 + 3))

        mocked_return_value = mock_subject.process('stuff', thing='hey')
        assert mocked_return_value == 5
