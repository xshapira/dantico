# Schema customization

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
