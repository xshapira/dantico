# Introspect the related objects

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
