import json
import typing

import pytest
from dantico import ModelSchema, SchemaFactory, model_validator
from dantico.exceptions import ConfigError
from django.db import models
from pydantic import Field

from tests.conf import JSON_FIELD_COMPATIBILITY, TEXT_CHOICES_COMPATIBILITY
from tests.models import Auction, User


class TestModelSchema:
    def test_schema_include_fields(self):
        class AuctionSchema(ModelSchema):
            class Config:
                model = Auction
                include = "__all__"

        assert AuctionSchema.schema() == {
            "title": "AuctionSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "category_id": {"title": "Category", "type": "integer"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

        class AuctionSchema2(ModelSchema):
            class Config:
                model = Auction
                include = ["title", "start_date", "end_date"]

        assert AuctionSchema2.schema() == {
            "title": "AuctionSchema2",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

    @pytest.mark.skip(reason="Not implemented this yet")  # pragma: no cover
    def test_reverse_one_to_one(self):
        class UserDepthSchema(ModelSchema):
            class Config:
                model = User
                include = ["full_name", "agency_admin"]

        assert UserDepthSchema.schema()

    @pytest.mark.skipif(
        not TEXT_CHOICES_COMPATIBILITY,
        reason="models.TextChoices introduced in django 3.0",
    )
    def test_schema_default_null(self):
        from .models import UserTier

        class UserTierSchema(ModelSchema):
            class Config:
                model = UserTier
                include = "__all__"

        assert UserTierSchema.schema() == {
            "title": "UserTierSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "name": {"title": "Name", "maxLength": 10, "type": "string"},
                "level": {
                    "title": "Level",
                    "default": "level-0",
                    "allOf": [{"$ref": "#/definitions/LevelEnum"}],
                },
            },
            "required": ["name"],
            "definitions": {
                "LevelEnum": {
                    "title": "LevelEnum",
                    "description": "An enumeration.",
                    "enum": ["level-0", "level-1"],
                }
            },
        }

    def test_schema_depth(self):
        class UserDepthSchema(ModelSchema):
            class Config:
                model = User
                include = "__all__"
                depth = 1

        assert UserDepthSchema.schema() == {
            "title": "UserDepthSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "full_name": {"title": "Full Name", "maxLength": 50, "type": "string"},
                "age": {"title": "Age", "type": "integer"},
                "profile": {
                    "title": "Profile",
                    "allOf": [{"$ref": "#/definitions/Profile"}],
                },
                "tier": {
                    "title": "Tier",
                    "allOf": [{"$ref": "#/definitions/UserType"}],
                },
                "groups": {
                    "title": "Groups",
                    "type": "array",
                    "items": {"$ref": "#/definitions/Group"},
                },
            },
            "required": ["full_name", "age", "profile", "groups"],
            "definitions": {
                "Profile": {
                    "title": "Profile",
                    "type": "object",
                    "properties": {
                        "id": {"title": "Id", "extra": {}, "type": "integer"},
                        "address": {"title": "Address", "type": "string"},
                        "dob": {
                            "title": "Dob",
                            "type": "string",
                            "format": "date-time",
                        },
                    },
                    "required": ["address"],
                },
                "UserType": {
                    "title": "UserType",
                    "type": "object",
                    "properties": {
                        "id": {"title": "Id", "extra": {}, "type": "integer"},
                        "name": {"title": "Name", "maxLength": 50, "type": "string"},
                    },
                    "required": ["name"],
                },
                "Group": {
                    "title": "Group",
                    "type": "object",
                    "properties": {
                        "id": {"title": "Id", "extra": {}, "type": "integer"},
                        "name": {"title": "Name", "maxLength": 10, "type": "string"},
                    },
                    "required": ["name"],
                },
            },
        }

    def test_schema_exclude_fields(self):
        class AuctionSchema3(ModelSchema):
            class Config:
                model = Auction
                exclude = ["id", "category"]

        assert AuctionSchema3.schema() == {
            "title": "AuctionSchema3",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

    def test_schema_optional_fields(self):
        class AuctionSchema4(ModelSchema):
            class Config:
                model = Auction
                include = "__all__"
                optional = "__all__"

        assert AuctionSchema4.schema() == {
            "title": "AuctionSchema4",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {
                    "title": "Title",
                    "extra": {},
                    "maxLength": 100,
                    "type": "string",
                },
                "category_id": {"title": "Category", "extra": {}, "type": "integer"},
                "start_date": {
                    "title": "Start Date",
                    "extra": {},
                    "type": "string",
                    "format": "date",
                },
                "end_date": {
                    "title": "End Date",
                    "extra": {},
                    "type": "string",
                    "format": "date",
                },
            },
        }

        class AuctionSchema5(ModelSchema):
            class Config:
                model = Auction
                include = ["id", "title", "start_date"]
                optional = [
                    "start_date",
                ]

        assert AuctionSchema5.schema() == {
            "title": "AuctionSchema5",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "extra": {},
                    "type": "string",
                    "format": "date",
                },
            },
            "required": [
                "id",
                "title",
            ],  # noqa: E231
        }

    def test_schema_custom_fields(self):
        class AuctionSchema6(ModelSchema):
            custom_field1: str
            custom_field2: int = 1
            custom_field3 = ""
            _custom_field4 = []  # ignored by pydantic

            class Config:
                model = Auction
                exclude = ["id", "category"]

        assert AuctionSchema6.schema() == {
            "title": "AuctionSchema6",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
                "custom_field1": {"title": "Custom Field1", "type": "string"},
                "custom_field3": {
                    "title": "Custom Field3",
                    "default": "",
                    "type": "string",
                },
                "custom_field2": {
                    "title": "Custom Field2",
                    "default": 1,
                    "type": "integer",
                },
            },
            "required": ["custom_field1", "title", "start_date", "end_date"],
        }

    def test_model_validator(self):
        class AuctionSchema(ModelSchema):
            class Config:
                model = Auction
                include = [
                    "title",
                    "start_date",
                ]

            @model_validator("title")
            def validate_title(cls, value):
                return f"{value} - value cleaned"

        auction = AuctionSchema(start_date="2022-07-06", title="MacBook Pro Mid 2015")
        assert "value cleaned" in auction.title

        class AuctionSchema2(ModelSchema):
            custom_field: str

            class Config:
                model = Auction
                include = [
                    "title",
                    "start_date",
                ]

            @model_validator("title", "custom_field")
            def validate_title(cls, value):
                return f"{value} - value cleaned"

        auction2 = AuctionSchema2(
            start_date="2022-07-06",
            title="MacBook Pro Mid 2015",
            custom_field="some custom field",
        )
        assert "value cleaned" in auction2.title
        assert "value cleaned" in auction2.custom_field

    def test_invalid_fields_inputs(self):
        with pytest.raises(ConfigError):

            class AuctionSchema1(ModelSchema):
                class Config:
                    model = Auction
                    include = ["ab", "bc"]

        with pytest.raises(ConfigError):

            class AuctionSchema2(ModelSchema):
                class Config:
                    model = Auction
                    exclude = ["ab", "bc"]

        with pytest.raises(ConfigError):

            class AuctionSchema3(ModelSchema):
                class Config:
                    model = Auction
                    optional = ["ab", "bc"]

    def test_model_validator_not_used(self):
        with pytest.raises(ConfigError):

            class AuctionSchema1(ModelSchema):
                class Config:
                    model = Auction
                    exclude = [
                        "title",
                    ]

                @model_validator("start_date", "title")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"  # pragma: no cover

        with pytest.raises(ConfigError):

            class AuctionSchema2(ModelSchema):
                class Config:
                    model = Auction
                    include = [
                        "title",
                    ]

                @model_validator("title", "invalid_field")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"  # pragma: no cover

    def test_factory_functions(self):
        auction_schema = SchemaFactory.create_schema(
            model=Auction, name="AuctionSchema"
        )
        print(json.dumps(auction_schema.schema(), sort_keys=False, indent=4))
        assert auction_schema.schema() == {
            "title": "AuctionSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "category_id": {"title": "Category", "type": "integer"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

    def get_new_auction(self, title):
        auction = Auction(title=title)
        auction.save()
        return auction

    @pytest.mark.django_db
    def test_getter_functions(self):
        class AuctionSchema(ModelSchema):
            class Config:
                model = Auction
                include = ["title", "category", "id"]

        auction = self.get_new_auction(title="MacBook Pro")
        json_auction = AuctionSchema.from_orm(auction)

        assert json_auction.dict() == {
            "id": 1,
            "title": "MacBook Pro",
            "category": None,
        }
        json_auction.title = "Auction ended"

        json_auction.apply_to_model(auction)
        assert auction.title == "Auction ended"

    def test_include_and_exclude(self):
        with pytest.raises(ConfigError):
            SchemaFactory.create_schema(
                model=Auction,
                name="AuctionSchema",
                fields=["title"],
                exclude=["start_date"],
            )

    def test_schema_with_existing_model(self):
        AuctionSchema1 = SchemaFactory.create_schema(
            model=Auction,
            name="AuctionSchema2",
            fields=["title"],
        )
        AuctionSchema2 = SchemaFactory.create_schema(
            model=Auction,
            name="AuctionSchema2",
            fields=["title"],
        )
        assert AuctionSchema1 == AuctionSchema2

    def test_validator_without_field(self):
        with pytest.raises(ConfigError):

            class AuctionSchema1(ModelSchema):
                class Config:
                    model = Auction
                    include = [
                        "title",
                    ]

                @model_validator()
                def validate_title(cls, value):  # pragma: no cover
                    return f"{value} - value cleaned"

    def test_pydantic_validator_decorator(self):
        with pytest.raises(ConfigError):

            class AuctionSchema(ModelSchema):
                class Config:
                    model = Auction
                    include = [
                        "title",
                    ]

                @model_validator
                def validate_title(cls, value):  # pragma: no cover
                    return f"{value} - value cleaned"

    def test_model_field_with_underscore(self):
        class Person(models.Model):
            _first_name = models.CharField(max_length=10)
            last_name = models.CharField(max_length=10)

        class PersonSchema(ModelSchema):
            class Config:
                model = Person

        assert list(PersonSchema.schema()["properties"].keys()) == ["id", "last_name"]

    def test_untouched(self):
        class UserSchema(ModelSchema):
            class Config:
                model = User
                include = ["full_name"]
                # keep_untouched = (property,)

            @property
            def something(self):
                return "something property"

        assert UserSchema(full_name="Alice B").something == "something property"

    def test_class_variable(self):
        class UserSchema(ModelSchema):
            cls_var: typing.ClassVar[int] = 123
            non_cls_var: int = 123

            class Config:
                model = User

        assert "cls_var" not in UserSchema.schema()["properties"].keys()

    def test_missing_model_key(self):
        with pytest.raises(ConfigError):

            class UserSchema(ModelSchema):
                class Config:
                    models = User  # it should be `model`

    def test_missing_django_model(self):
        with pytest.raises(ConfigError):

            class NonDjangoModel:
                age: int = 12

            class UserSchema(ModelSchema):
                class Config:
                    model = NonDjangoModel

    def test_default_factory(self):
        def default_factory_callable():
            return "something"

        class UserSchema(ModelSchema):
            full_name: str = Field(default_factory=default_factory_callable)

            class Config:
                model = User
                include = ["full_name"]

        assert UserSchema().dict()["full_name"] == "something"

    def test_root_type(self):
        with pytest.raises(ValueError):

            class UserSchema(ModelSchema):
                __root__: int = 123

                class Config:
                    model = User

    @pytest.mark.skipif(
        not JSON_FIELD_COMPATIBILITY,
        reason="models.JSONField introduced in django 3.1",
    )
    def test_json_field_with_null(self):
        from .models import JSONConfig

        class JSONConfigSchema(ModelSchema):
            class Config:
                model = JSONConfig

        assert JSONConfigSchema.schema() == {
            "title": "JSONConfigSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "config": {
                    "title": "Config",
                    "type": "string",
                    "format": "json-string",
                },
            },
        }

    def test_invalid(self):
        with pytest.raises(TypeError):

            class UserSchema(ModelSchema):
                extra_field: str = Field()

                class Config:
                    model = User

            class UserSchema2(UserSchema):
                extra_field = 123
