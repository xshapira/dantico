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

- **Field Validator**: Fields can be validated with Pydantic **[validator](https://pydantic-docs.helpmanual.io/usage/validators/)** or **[root_validator](https://pydantic-docs.helpmanual.io/usage/validators/)**.

## Requirements

- Python 3.7+
- Django 3.0+
- Pydantic 1.6+

## Installation

```
pip install dantico
```

## Usage

Assume we have the following user model definition:

```python
# models.py

from django.db import models


class User(models.Model):

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"

    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )

    username = models.CharField(max_length=20)
    age = models.IntegerField()
    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=10,
        blank=True,
    )
    password = models.CharField(max_length=100)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )
    languages = models.ManyToManyField(Language)

    def __str__(self):
        return self.name

```

Using the `ModelSchema` class will automatically generate schemas from our `User` model.

```python
# schemas.py

from dantico import ModelSchema
from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User


json_output = json.dumps(UserSchema.schema(), indent=4)
print(json_output)


# Output:
{
    "title": "UserSchema",
    "type": "object",
    "properties": {
        "id": {
            "title": "Id",
            "extra": {},
            "type": "integer"
        },
        "Username": {
            "title": "Username",
            "maxLength": 20,
            "type": "string"
        },
        "age": {
            "title": "Age",
            "type": "integer"
        },
        "gender": {
            "title": "Gender",
            "allOf": [
                {
                    "$ref": "#/definitions/GenderEnum"
                }
            ]
        },
        "password": {
            "title": "Password",
            "maxLength": 100,
            "type": "string"
        },
        "company_id": {
            "title": "Company",
            "type": "integer"
        },
        "languages": {
            "title": "Languages",
            "type": "array",
            "items": {
                "type": "integer"
            }
        }
    },
    "required": [
        "Username",
        "age",
        "password",
        "company_id",
        "languages"
    ],
    "definitions": {
        "GenderEnum": {
            "title": "GenderEnum",
            "description": "An enumeration.",
            "enum": [
                "male",
                "female",
                "other"
            ]
        }
    }
}
```

## License

This project is licensed under the terms of the MIT license.
