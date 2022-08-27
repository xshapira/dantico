
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

- Python 3.6+
- Django 2.2+
- Pydantic 1.6+

## Installation

```
pip install dantico
```

## Usage

Here are a few examples of what you can do with *dantico*:

### Basic

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

### Excluding and including model fields

By default *dantico* include all the fields from the Django model. As a rule of thumb, always use the `include` or `exclude` attribute to explicitly define a list of fields that you want to be visible in your API. **Note that you cannot use both at the same time**.

```python
# schemas.py

from dantico import ModelSchema
from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User
        exclude = ["password", "age"]


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
        "username": {
            "title": "Username",
            "maxLength": 20,
            "type": "string"
        },
        "gender": {
            "title": "Gender",
            "allOf": [
                {
                    "$ref": "#/definitions/GenderEnum"
                }
            ]
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
        "username",
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

An example of using `include`:

```python
# schemas.py

from dantico import ModelSchema
from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User
        include = ["username", "age", "company"]


json_output = json.dumps(UserSchema.schema(), indent=4)
print(json_output)


# Output:
{
    "title": "UserSchema",
    "type": "object",
    "properties": {
        "username": {
            "title": "Username",
            "maxLength": 20,
            "type": "string"
        },
        "age": {
            "title": "Age",
            "type": "integer"
        },
        "company_id": {
            "title": "Company",
            "type": "integer"
        }
    },
    "required": [
        "Username",
        "age",
        "company_id"
    ]
}

```

### Optional model fields

We can also specify model fields to mark as `optional`.

```python
# schemas.py

from dantico import ModelSchema
from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User
        exclude = ["password", "languages"]
        optional = ["age"] # 'age' schema field is now optional


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
        "username": {
            "title": "Username",
            "maxLength": 20,
            "type": "string"
        },
        "age": {
            "title": "Age",
            "extra": {},
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
        "company_id": {
            "title": "Company",
            "type": "integer"
        }
    },
    "required": [
        "username",
        "company_id"
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

### Introspect the related objects

The `depth` attribute lets us look into the Django model relations (many to one, one to one, many to many).

Consider the following models definitions:

```python
# models.py

from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=20)
    location = models.CharField(max_length=20)
    date_created = models.DateField()

    def __str__(self):
        return self.name


class Language(models.Model):

    name = models.CharField(max_length=20)
    creator = models.CharField(max_length=20)
    paradigm = models.CharField(max_length=20)
    date_created = models.DateField()

    def __str__(self):
        return self.name


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

Now let's add the `depth` attribute:

```python
# schemas.py

from dantico import ModelSchema
from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User
        exclude = ["password", "age", "gender"]
        optional = ["age"]
        depth = 1 # by default, depth = 0


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
        "username": {
            "title": "Username",
            "maxLength": 20,
            "type": "string"
        },
        "company": {
            "title": "Company",
            "allOf": [
                {
                    "$ref": "#/definitions/Company"
                }
            ]
        },
        "languages": {
            "title": "Languages",
            "type": "array",
            "items": {
                "$ref": "#/definitions/Language"
            }
        }
    },
    "required": [
        "username",
        "company",
        "languages"
    ],
    "definitions": {
        "Company": {
            "title": "Company",
            "type": "object",
            "properties": {
                "id": {
                    "title": "Id",
                    "extra": {},
                    "type": "integer"
                },
                "name": {
                    "title": "Name",
                    "maxLength": 20,
                    "type": "string"
                },
                "location": {
                    "title": "Location",
                    "maxLength": 20,
                    "type": "string"
                },
                "date_created": {
                    "title": "Date Created",
                    "type": "string",
                    "format": "date"
                }
            },
            "required": [
                "name",
                "location",
                "date_created"
            ]
        },
        "Language": {
            "title": "Language",
            "type": "object",
            "properties": {
                "id": {
                    "title": "Id",
                    "extra": {},
                    "type": "integer"
                },
                "name": {
                    "title": "Name",
                    "maxLength": 20,
                    "type": "string"
                },
                "creator": {
                    "title": "Creator",
                    "maxLength": 20,
                    "type": "string"
                },
                "paradigm": {
                    "title": "Paradigm",
                    "maxLength": 20,
                    "type": "string"
                },
                "date_created": {
                    "title": "Date Created",
                    "type": "string",
                    "format": "date"
                }
            },
            "required": [
                "name",
                "creator",
                "paradigm",
                "date_created"
            ]
        }
    }
}
```

### Schema customization

Docstrings and titles can be used as descriptive text in the schema output.

```python
# schemas.py

from pydantic import Field
from dantico import ModelSchema
from users.models import User


class UserSchema(ModelSchema):
    """My user model schema"""
    username: str = Field(
        title="The user's username",
        description="This is the user's username",
    )
    age: int = Field(
        None,
        title="The user's age",
        description="This is the user's age",
    )

    class Config:
        model = User
        exclude = ["password", "gender", "languages"]
        title = "User schema"


json_output = json.dumps(UserSchema.schema(), indent=4)
print(json_output)


# Output:
{
    "title": "User schema",
    "description": "My user model schema",
    "type": "object",
    "properties": {
        "username": {
            "title": "The user's username",
            "description": "This is the user's username",
            "type": "string"
        },
        "age": {
            "title": "The user's age",
            "description": "This is the user's age",
            "type": "integer"
        },
        "id": {
            "title": "Id",
            "extra": {},
            "type": "integer"
        },
        "company_id": {
            "title": "Company",
            "type": "integer"
        }
    },
    "required": [
        "username",
        "company_id"
    ]
}
```

### Field validator

Custom validation is not an easy task in this case. But we still can achieve it by using threads.

Because we define a validator to validate fields on inheriting models, we should set `check_fields=False` on the validator. More information can be found [here](https://pydantic-docs.helpmanual.io/usage/validators/).

```python
# schemas.py
import asyncio
import concurrent.futures

from asgiref.sync import sync_to_async
from dantico import ModelSchema
from pydantic import validator

from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User
        exclude = ["password"]

    @validator("username", check_fields=False)
    def validate_username(cls, v):
        """
        Here we are using async method as validator. Because there is
        already an event loop (using FastAPI), we need to start another thread.

        :param cls: Access the class of the object that is being validated
        :param v: Validate the value
        :return: The result of the username_must_be_unique function
        """

        @sync_to_async
        def username_must_be_unique():
            if User.objects.filter(username__icontains=v).exists():
                raise ValueError("username already exists")
            return v

        # A way to run async code in a sync environment.
        pool = concurrent.futures.ThreadPoolExecutor(1)
        result = pool.submit(asyncio.run, username_must_be_unique()).result()

        return result
```

## License

This project is licensed under the terms of the MIT license.
