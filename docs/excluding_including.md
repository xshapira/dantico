# Excluding and including model fields

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
