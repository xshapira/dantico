import json

import pytest
from dantico import ModelSchema
from django.db import models
from pydantic import ValidationError


class Programmer(models.Model):

    FRAMEWORK_CHOICES = [
        ("1", "Django"),
        ("2", "FastAPI"),
        ("3", "Flask"),
    ]

    framework = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES, default="2")


class ProgrammerEmail(models.Model):
    email = models.EmailField(null=False, blank=False)


class TestCustomFields:
    def test_enum_field(self):
        class ProgrammerSchema(ModelSchema):
            class Config:
                model = Programmer
                include = "__all__"

        print(json.dumps(ProgrammerSchema.schema(), sort_keys=False, indent=4))
        assert ProgrammerSchema.schema() == {
            "title": "ProgrammerSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "framework": {
                    "title": "Framework",
                    "default": "2",
                    "allOf": [{"$ref": "#/definitions/FrameworkEnum"}],
                },
            },
            "definitions": {
                "FrameworkEnum": {
                    "title": "FrameworkEnum",
                    "description": "An enumeration.",
                    "enum": ["1", "2", "3"],
                }
            },
        }
        schema_instance = ProgrammerSchema(framework="2")
        assert str(schema_instance.json()) == '{"id": null, "framework": "2"}'
        with pytest.raises(ValidationError):
            ProgrammerSchema(framework="something")

    def test_email_field(self):
        class ProgrammerEmailSchema(ModelSchema):
            class Config:
                model = ProgrammerEmail
                include = "__all__"

        print(json.dumps(ProgrammerEmailSchema.schema(), sort_keys=False, indent=4))
        assert ProgrammerEmailSchema.schema() == {
            "title": "ProgrammerEmailSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "email": {"title": "Email", "type": "string", "format": "email"},
            },
            "required": ["email"],
        }
        assert (
            str(ProgrammerEmailSchema(email="email@example.com").json())
            == '{"id": null, "email": "email@example.com"}'
        )
        with pytest.raises(ValidationError):
            ProgrammerEmailSchema(email="emailexample.com")
