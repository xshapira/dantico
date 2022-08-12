
# dantico

Tools to convert Django ORM models to Pydantic models.

[![GitHub Actions (Test)](https://github.com/xshapira/dantico/workflows/Test/badge.svg)](https://github.com/xshapira/dantico)
[![Codecov](https://img.shields.io/codecov/c/gh/xshapira/dantico?color=%2334D058)](https://codecov.io/gh/xshapira/dantico)
[![PyPI version](https://badge.fury.io/py/dantico.svg)](https://badge.fury.io/py/dantico)
[![Downloads](https://pepy.tech/badge/dantico/month)](https://pepy.tech/project/dantico)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/dantico.svg)](https://pypi.python.org/pypi/dantico)
[![PyPI Supported Django Versions](https://img.shields.io/pypi/djversions/dantico.svg)](https://docs.djangoproject.com/en/dev/releases/)

The key features are:

- **Custom Field Support**: Create Pydantic Schemas from Django Models with default field type validations out of the box.

- **Field Validator**: Fields can be validated with `model_validator` just like Pydantic **[validator](https://pydantic-docs.helpmanual.io/usage/validators/)** or **[root_validator](https://pydantic-docs.helpmanual.io/usage/validators/)**.

## Requirements

- Python 3.6+
- Django 2.2+
- Pydantic 1.6+

## Installation

```
pip install dantico
```

## Usage

Here are a few examples of what you can do with **dantico**:

### Field Validator

`model_validator(*args, **kwargs)` is a substitute for Pydantic [validator](https://pydantic-docs.helpmanual.io/usage/validators/) used for pre and post fields validation.
Their functionalities are the same. More information can be found [here](https://pydantic-docs.helpmanual.io/usage/validators/).

```Python
from users.models import User
from dantico import ModelSchema, model_validator


class UserSchema(ModelSchema):
    class Config:
        model = User
        # Fields to include, by default include all the fields
        # from the Django model
        include = ["username", "email", "password"]

    @model_validator("username")
    def validate_unique_username(cls, value_data: str) -> str:
        if User.objects.filter(username__icontains=value_data).exists():
            raise ValueError("Username exists")
        return value_data
```

### Generate schema instance

You can generate a schema instance from your django model instance using `from_orm(cls, obj: Any)`

```Python
from typings import Optional
from users.models import User
from dantico import ModelSchema, model_validator

new_user = User.objects.create_user(
    username="Max",
    email="max@winoutt.com",
    password="password",
    first_name="Max",
    last_name="Shapira",
)


class UserSchema(ModelSchema):
    class Config:
        model = User
        # Include all the fields from a model except 'password' field
        exclude = ["password"]

schema = UserSchema.from_orm(new_user)

print(schema.json(indent=2)
{
    "id": 1,
    "first_name": "Max",
    "last_name": "Shapira",
    "email": "max@winoutt.com",
    "username": "Max",
}
```

### From ModelSchema to Django Model

You can transfer data from your ModelSchema to Django Model instance using `apply(self, model_instance, **kwargs)`.
The `apply` function uses Pydantic model `.dict` function, `dict` function filtering what can be passed as `kwargs` to the `.apply` function.

For more information, check out [Pydantic model export](https://pydantic-docs.helpmanual.io/usage/exporting_models/).

```Python
from typings import Optional
from users.models import User
from dantico import ModelSchema, model_validator

new_user = User.objects.create_user(
      username="max",
      email="max@winoutt.com",
      password="password",
  )


class UpdateUserSchema(ModelSchema):
    class Config:
        model = User
        include = ["first_name", "last_name", "username"]
        optional = ["username"]  # 'username' is now optional

schema = UpdateUserSchema(first_name="Max", last_name="Shapira")
schema.apply(new_user, exclude_none=True)

assert new_user.first_name == "Max" # True
assert new_user.username == "max" # True
```

## License

This project is licensed under the terms of the MIT license.
