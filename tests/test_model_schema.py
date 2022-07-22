import json

import pytest
from dantico import ModelSchema, SchemaFactory, model_validator
from dantico.exceptions import ConfigError

from tests.models import Auction


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

    def test_schema_depth(self):
        class AuctionDepthSchema(ModelSchema):
            class Config:
                model = Auction
                include = "__all__"
                depth = 1

        assert AuctionDepthSchema.schema() == {
            "title": "AuctionDepthSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "category": {
                    "title": "Category",
                    "allOf": [{"$ref": "#/definitions/Category"}],
                },
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
            "definitions": {
                "Category": {
                    "title": "Category",
                    "type": "object",
                    "properties": {
                        "id": {"title": "Id", "extra": {}, "type": "integer"},
                        "name": {"title": "Name", "maxLength": 100, "type": "string"},
                        "start_date": {
                            "title": "Start Date",
                            "type": "string",
                            "format": "date",
                        },
                        "end_date": {
                            "title": "End Date",
                            "type": "string",
                            "format": "date",
                        },
                    },
                    "required": ["name", "start_date", "end_date"],
                }
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

                @model_validator("title")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"

        with pytest.raises(ConfigError):

            class AuctionSchema2(ModelSchema):
                class Config:
                    model = Auction
                    include = [
                        "title",
                    ]

                @model_validator("title", "invalid_field")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"

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
