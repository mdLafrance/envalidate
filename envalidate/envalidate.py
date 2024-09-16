"""Core library functionality.
"""

import os

from pydantic import BaseModel, model_validator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .errors import MissingEnvironmentError


class Envalidator(BaseModel):
    """`Envalidator` provides a way to validate and type check environment variables at runtime.

    Create a subclass of `Envalidator`, and define the fields that should be automatically parsed and validated from the current environment. Constructing an instance of this subclass will source values from the environment, and throw the appropriate exceptions if expected values are missing or are of the incorrect type.

    See the readme for more information.
    https://github.com/mdlafrance/envalidate

    Example:
    ```python
    from typing import Annotated

    from envalidate import Envalidator

    class MyEnvironment(Envalidator):
        # This will be sourced from the environment variable API_KEY.
        api_key: str

        # This will be sourced from the environment variable X_SERVER_URL, and default to localhost
        server_url: Annotated[str, "X_SERVER_URL"] = "https://localhost:8080"

        # This will be coerced to an integer, and defaults to 8000
        timeout: Annotated[int, "API_TIMEOUT"] = 8000

    # If the environment is incomplete, this will throw an exception.
    env = MyEnvironment()

    ...

    client = new Client(env.server_url, env.api_key)
    ```
    """

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
    """Extract the target envirnment variable from the pydantic field.

    This is currently a stub, but more complex logic may be added in the future.

    Args:
        field (FieldInfo): The pydantic field to extract the environment variable from.

    Returns:
        str | None: The target environment variable, or None if no environment variable is specified.
    """
    if field.metadata:
        return field.metadata[0]
