<h1 align=center>
  
  :lock: :snake: **envalidate**
  
</h1>

<div align=center>

  [![Pipeline](https://github.com/mdLafrance/envalidate/actions/workflows/pipeline.yml/badge.svg)](https://github.com/mdLafrance/envalidate/actions/workflows/pipeline.yml)
  [![PyPI version](https://badge.fury.io/py/envalidate.svg)](https://badge.fury.io/py/envalidate)
  [![Coverage Status](https://coveralls.io/repos/github/mdLafrance/envalidate/badge.svg?branch=update/base-functionality)](https://coveralls.io/github/mdLafrance/envalidate?branch=update/base-functionality)
  
</div>


# About

`envalidate` ensures that your environment variables in python are always valid, and totally type safe. 

By defining a datastruct up front to describe the shape of your environment, you can be sure that you won't run into any unexpected behavior later on. Instantiations of your environment object will immediately fail if the shape of the environment doesn't match what you have defined.

```python
# Dangerous! 
# Is this value a string? Is it None? Are we about to fall over from a KeyError?
env_setting = os.getenv["ENV_SETTING"]
some_function(env_setting) 
```
```python
# Better!
# All environment values will be type checked, and can have docstrings.
class MyEnvironment(Envalidator):
    env_setting: Annotated[int, "ENV_SETTING"]
    """This docstring is visible in your IDE."""

env = MyEnvironment() # This will throw an exception if the environment doesn't match

...

some_function(env.env_setting)

```

<br />

The `Envalidator` class is built on top of [pydantic](https://docs.pydantic.dev/), and it's usage should be familiar to users of that library.

<br />

# Installation
`envalidate` can be installed with pip:
```bash
pip install envalidate
```

<br />

# Quickstart
To use `envalidate` in your project, simply subclass `Envalidator`, and define the shape of your environment. 

The following example covers most of the available functionality, and features that will be useful when describing an environment. It is recommended to instantiate one instance of your environment, and consume it wherever is necessary. Using `Envalidator` in this way ensures that any environment mismatches are caught at early as possible.



```python
from envalidate import Envalidator
from typing import Annotated

class MyEnvironment(Envalidator):
    api_key: str
    """API key for X service."""

    deployment_stage: Literal["dev", "prod"] = "dev"
    """The deployment stage of the app. This is set automatically by the CI/CD pipeline."""

    service_timeout: Annotated[int, "X_SERVICE_TIMEOUT"] = 8000
    """The timeout for the X service (milliseconds)."""

    some_optional_field: Annotated[str, "FOO"] = None

env = MyEnvironment(
    api_key="api-key-override"
)
```
> The actual names and values shown here are just for example purposes

<br />

# Defining an environment
### Default behavior
The default behavior of a field defined in your environment is to source the environment variable with the **uppercase name of the field**.  
In the example above, the `api_key` field will source the environment variable `API_KEY`. If the associated environment variable could not be found, a `MissingEnvironmentVariable` exception will be raised.

### Specifying a different environment variable
If you want to source a different environment variable, you can use an `Annotated` type to specify the specific variable to source. 

In the above example, the `service_timeout` field is defined as `Annotated[int, "X_SERVICE_TIMEOUT"]`, meaning
- The type of the field is an int
- The field will be sourced from the environment variable `X_SERVICE_TIMEOUT`

> [!NOTE] Manually specified environment variables are **case sensitive**

### Specifying complex types
Just like regular [pydantic](https://docs.pydantic.dev/) fields, you can use python type annotations to define any kind of data you'd like.

In the above example, the `deployment_stage` field is defined as `Literal["dev", "prod"]`, which will:
- Source the environment variable `DEPLOYMENT_STAGE`
- If the value of this environment variable is not one of the two options, an exception will be raised.

### Default values and optional values
Fields can be provided with default values that will be used in case the associated environment variable is not found.

Fields can be marked as optional by giving them a default value of `None`.

### Overriding values
If you want to override the value of a field regardless of the environment, you can pass key/value pairs to the constructor of your environment object:

```python
env = MyEnvironment(api_key="my-api-key")
```

<br />

## Pyright errors
If using pyright as your LSP, it might start commplaining about missing fields. This is an issue on the pydantic side, and the discussion is still ongoing.  

If this is the case for you, there is a utility factory function that can be used to bypass these errors:

```python
env = MyEnvironment(foo="bar") # pyright might be complaining
env = MyEnvironment.from_env(foo="bar") # pyright is happy again
```

These methods of instantiation are identical, and have no effect on the environment object itself. The pyright error will also not stop you from running your code, but it might be annoying.

<br />

# Design
* This library was inspired by the `zod` workflow to define environment schemas in `typescript`. I wanted to be able to use something similar in my python workflows
* This library is designed with the principles of **fail fast, fail early** in mind - if your environment is incompatible with your code, an exception should be raised as soon as possible
