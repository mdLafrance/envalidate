import os

from types import NoneType
from typing import Any, Union

from pydantic import BaseModel, model_validator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .errors import MissingEnvironmentError


class Envalidator(BaseModel):
    @classmethod
    def from_env(cls, **kwargs):
        return cls(**kwargs)

    @model_validator(mode="before")
    @classmethod
    def validate_env(cls, data):
        for field_name, field in cls.model_fields.items():
            # Users have manually specified a default value for this field.
            if field_name in data:
                continue

            target_env_var = get_env_var_from_field(field) or field_name.upper()

            value = os.getenv(target_env_var) or field.default

            # NOTE: This is an annoying side effect of pydantic's `field.default` behavior.
            # If a field doesn't have a default, accessing `field.default` doesn't produce
            # `None`, but instead a custom type where `bool(PydanticUndefined) == True`.
            if value == PydanticUndefined:
                value = None

            if not value and field.is_required():
                raise MissingEnvironmentError(
                    f"Missing environment variable: {target_env_var}"
                )

            data[field_name] = value

        return data


def get_env_var_from_field(field: FieldInfo) -> str | None:
    if field.metadata:
        return field.metadata[0]
