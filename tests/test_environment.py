import os

from pydantic import ValidationError
import pytest

from typing import Annotated, Literal
from unittest.mock import patch

from envalidate import Envalidator, MissingEnvironmentError


@patch.dict(os.environ, {"FOO": "foo", "BAR_KEY": "bar"})
def test_parse_basic_environment():
    class BasicEnvironment(Envalidator):
        foo: str
        bar: Annotated[str, "BAR_KEY"]
        baz: str = "Default baz"

    env = BasicEnvironment.from_env()

    assert(env.foo == "foo")
    assert(env.bar == "bar")
    assert(env.baz == "Default baz")


@patch.dict(os.environ, {"FOO": "foo", "BAR_KEY": "bar"})
def test_override_values():
    class OverrideEnvironment(Envalidator):
        foo: str
        """Foo string!"""
        bar: Annotated[str, "BAR_KEY"] = "Default bar"


    env = OverrideEnvironment.from_env(foo="new foo", bar="new bar")

    assert(env.foo == "new foo")
    assert(env.bar == "new bar")


@patch.dict(os.environ, {})
def test_failure_on_missing_environment():
    class MissingEnvironment(Envalidator):
        foo: str

    with pytest.raises(MissingEnvironmentError):
        MissingEnvironment.from_env()

    assert(MissingEnvironment.from_env(foo="foo").foo == "foo")


def test_literal_strings_parsed_correctly():
    class LiteralEnvironment(Envalidator):
        foo: Literal["foo", "bar"]

    with patch.dict(os.environ, {"FOO": "foo"}):
        assert(LiteralEnvironment.from_env().foo == "foo")

    with patch.dict(os.environ, {"FOO": "NOT_VALID"}):
        with pytest.raises(ValidationError):
            LiteralEnvironment.from_env()


def test_integers_coerced_correctly():
    class IntegerEnvironment(Envalidator):
        foo: int
        bar: int = 10
        baz: Annotated[int, "BAZ_KEY"]

    with patch.dict(os.environ, {"FOO": "10", "BAZ_KEY": "20"}):
        env = IntegerEnvironment.from_env()

        assert(env.foo == 10)
        assert(env.bar == 10)
        assert(env.baz == 20)
