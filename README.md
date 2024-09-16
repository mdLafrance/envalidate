<h1 align=center>
  
  :lock: :snake: **envalidate**
  
</h1>

<div align=center>

  [![Pipeline](https://github.com/mdLafrance/envalidate/actions/workflows/pipeline.yml/badge.svg)](https://github.com/mdLafrance/envalidate/actions/workflows/pipeline.yml)
  [![PyPI version](https://badge.fury.io/py/envalidate.svg)](https://badge.fury.io/py/envalidate)
  [![Coverage Status](https://coveralls.io/repos/github/mdLafrance/envalidate/badge.svg?branch=update/base-functionality)](https://coveralls.io/github/mdLafrance/envalidate?branch=update/base-functionality)
  
</div>


# About

`envalidate` ensures that your environment variables are always valid, and totally type safe. By defining a datastruct up front to describe the shape of your environment, you can be 100% sure that it will work as expected.

<br />

```python
# Dangerous! 
# Is it a string? Is it None? Are we about to fall over from a KeyError?

env_setting = os.getenv["ENV_SETTING"]
some_function(env_setting) 
```
```python
# Better!
class MyEnvironment(Envalidator):
    env_setting: Annotated[int, "ENV_SETTING"]
    """This docstring is visible in your IDE."""

env = MyEnvironment()

...

some_function(env.env_setting)

```

<br />

# Installation
`envalidate` can be installed with pip:
```bash
pip install envalidate
```

<br />

# Quickstart
To use `envalidate` in your project, simply subclass `Envalidator`, and define the shape of your environment. 

The following example covers most of the available functionality, and features that will be useful when describing an environment. 



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

env = MyEnvironment()
```
> The actual names and values shown here are just for example purposes


### `api_key`
When no additional meta information is provided, the environment variable used to source this field will be the **uppercase name of the field** - in this case **API_KEY**.

### `deployment_stage`
Default values can be provided for fields, like in the case of `deployment_stage`, which defaults to `"dev"`.
Notice that this field is annotated with `Literal["dev", "prod"]`, which means that the value of this field must be one of the two options. An exception will be raised if the parsed value is not one of these two. 

### `service_timeout`
For cases where the field name and target environment variable are unrelated, you specify the name of the environment variable to source by using an `Annotated` field, in which the annotation is the name of the environment variable. In this case, the environment variable to source will be **X_SERVICE_TIMEOUT**.

This field is also marked as type `int`, which means that the value of this field will be parsed as an integer.

### `some_optional_field`
This field is marked as type `str`, however, it has a default value of `None` meaning it is an optional field.

### `env`
When instantiating an instance of your environment, all fields are sourced, and verified for type correctness from the current environment variables. 

This instance can be safely consumed elsewhere in your application, since all fields have already been parsed

# Design
* This library was inspired by the `zod` workflow to define environment schemas in `typescript`. I wanted to be able to use something similar in my python workflows
* This library is designed with the principles of **fail fast, fail early** in mind - if your environment is incompatible with your code, an exception should be raised as soon as possible
