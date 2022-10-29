# Optional model fields

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
