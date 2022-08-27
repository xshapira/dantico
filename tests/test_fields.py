import json
from unittest.mock import Mock

import django
import pytest
from dantico import ModelSchema
from dantico.exceptions import ConfigError

# from django.contrib.postgres import fields as ps_fields
from django.db import models
from django.db.models import Manager

from tests.models import Auction


def test_inheritance():
    class ParentModel(models.Model):
        parent_field = models.CharField()

        class Meta:
            app_label = "tests"

    class ChildModel(ParentModel):
        child_field = models.CharField()

        class Meta:
            app_label = "tests"

    class ChildSchema(ModelSchema):
        class Config:
            model = ChildModel

    print(ChildSchema.schema())

    assert ChildSchema.schema() == {
        "title": "ChildSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "parent_field": {"title": "Parent Field", "type": "string"},
            "parentmodel_ptr_id": {
                "title": "Parentmodel Ptr",
                "type": "integer",
                "extra": {},
            },
            "child_field": {"title": "Child Field", "type": "string"},
        },
        "required": ["id", "parent_field", "child_field"],
    }


def test_all_fields():
    # Test all except relational field.

    class AllFields(models.Model):
        big_integer_field = models.BigIntegerField()
        binary_field = models.BinaryField()
        boolean_field = models.BooleanField()
        char_field = models.CharField()
        comma_separated_integer_field = models.CommaSeparatedIntegerField()
        date_field = models.DateField()
        date_time_field = models.DateTimeField()
        decimal_field = models.DecimalField()
        duration_field = models.DurationField()
        email_field = models.EmailField()
        file_field = models.FileField()
        file_path_field = models.FilePathField()
        float_field = models.FloatField()
        generic_ip_address_field = models.GenericIPAddressField()
        ip_address_field = models.IPAddressField()
        image_field = models.ImageField()
        integer_field = models.IntegerField()
        null_boolean_field = models.NullBooleanField()
        positive_integer_field = models.PositiveIntegerField()
        positive_small_integer_field = models.PositiveSmallIntegerField()
        slug_field = models.SlugField()
        small_integer_field = models.SmallIntegerField()
        text_field = models.TextField()
        time_field = models.TimeField()
        url_field = models.URLField()
        uuid_field = models.UUIDField()
        # arrayfield = ps_fields.ArrayField(models.CharField())
        # cicharfield = ps_fields.CICharField()
        # ciemailfield = ps_fields.CIEmailField()
        # citextfield = ps_fields.CITextField()
        # hstorefield = fields.HStoreField()
        # jsonfield = ps_fields.JSONField()
        # rangefield = fields.RangeField()

        class Meta:
            app_label = "tests"

    class AllFieldsSchema(ModelSchema):
        class Config:
            model = AllFields

    # print(SchemaCls.schema())
    assert AllFieldsSchema.schema() == {
        "title": "AllFieldsSchema",
        "type": "object",
        "properties": {
            "id": {"extra": {}, "title": "Id", "type": "integer"},
            "big_integer_field": {"title": "Big Integer Field", "type": "integer"},
            "binary_field": {
                "title": "Binary Field",
                "type": "string",
                "format": "binary",
            },
            "boolean_field": {"title": "Boolean Field", "type": "boolean"},
            "char_field": {"title": "Char Field", "type": "string"},
            "comma_separated_integer_field": {
                "title": "Comma Separated Integer Field",
                "type": "string",
            },
            "date_field": {"title": "Date Field", "type": "string", "format": "date"},
            "date_time_field": {
                "title": "Date Time Field",
                "type": "string",
                "format": "date-time",
            },
            "decimal_field": {"title": "Decimal Field", "type": "number"},
            "duration_field": {
                "title": "Duration Field",
                "type": "number",
                "format": "time-delta",
            },
            "email_field": {
                "title": "Email Field",
                "format": "email",
                "type": "string",
            },
            "file_field": {"title": "File Field", "type": "string"},
            "file_path_field": {"title": "File Path Field", "type": "string"},
            "float_field": {"title": "Float Field", "type": "number"},
            "generic_ip_address_field": {
                "title": "Generic Ip Address Field",
                "type": "string",
                "format": "ipvanyaddress",
            },
            "ip_address_field": {
                "title": "Ip Address Field",
                "type": "string",
                "format": "ipvanyaddress",
            },
            "image_field": {"title": "Image Field", "type": "string"},
            "integer_field": {"title": "Integer Field", "type": "integer"},
            "null_boolean_field": {"title": "Null Boolean Field", "type": "boolean"},
            "positive_integer_field": {
                "title": "Positive Integer Field",
                "type": "integer",
            },
            "positive_small_integer_field": {
                "title": "Positive Small Integer Field",
                "type": "integer",
            },
            "slug_field": {"title": "Slug Field", "type": "string"},
            "small_integer_field": {"title": "Small Integer Field", "type": "integer"},
            "text_field": {"title": "Text Field", "type": "string"},
            "time_field": {"title": "Time Field", "type": "string", "format": "time"},
            "url_field": {
                "title": "Url Field",
                "type": "string",
                "format": "uri",
                "maxLength": 65536,
                "minLength": 1,
            },
            "uuid_field": {"title": "Uuid Field", "type": "string", "format": "uuid"},
            # "arrayfield": {"title": "Arrayfield", "type": "array"},
            # "cicharfield": {"title": "Cicharfield", "type": "string"},
            # "ciemailfield": {
            #     "title": "Ciemailfield",
            #     "maxLength": 254,
            #     "type": "string",
            # },
            # "citextfield": {"title": "Citextfield", "type": "string"},
            # "hstorefield": {"title": "Hstorefield", "type": "object"},
            # "jsonfield": {"title": "Jsonfield", "type": "object"},
            # "rangefield": {"title": "Rangefield", "type": "object"},
        },
        "required": [
            "big_integer_field",
            "binary_field",
            "boolean_field",
            "char_field",
            "comma_separated_integer_field",
            "date_field",
            "date_time_field",
            "decimal_field",
            "duration_field",
            "email_field",
            "file_field",
            "file_path_field",
            "float_field",
            "generic_ip_address_field",
            "ip_address_field",
            "image_field",
            "integer_field",
            "null_boolean_field",
            "positive_integer_field",
            "positive_small_integer_field",
            "slug_field",
            "small_integer_field",
            "text_field",
            "time_field",
            "url_field",
            "uuid_field",
            # "arrayfield",
            # "cicharfield",
            # "ciemailfield",
            # "citextfield",
            # "hstorefield",
            # "jsonfield",
            # "rangefield",
        ],
    }


def test_fields_with_choices():
    class ChoiceFieldsModel(models.Model):
        FRAMEWORK_CHOICES = [
            ("1", "Django"),
            ("2", "FastAPI"),
            ("3", ("Flask", "FLASK")),
        ]
        char_field = models.CharField(choices=FRAMEWORK_CHOICES)

    class ChoiceFieldsSchema(ModelSchema):
        class Config:
            model = ChoiceFieldsModel

    assert ChoiceFieldsSchema.schema() == {
        "title": "ChoiceFieldsSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "extra": {}, "type": "integer"},
            "char_field": {
                "title": "Char Field",
                "allOf": [{"$ref": "#/definitions/CharFieldEnum"}],
            },
        },
        "required": ["char_field"],
        "definitions": {
            "CharFieldEnum": {
                "title": "CharFieldEnum",
                "description": "An enumeration.",
                "enum": ["1", "2", "3"],
            }
        },
    }


def test_fields_with_include_and_exclude():
    with pytest.raises(ConfigError):

        class AuctionSchema(ModelSchema):
            class Config:
                model = Auction
                include = ["title"]
                exclude = ["start_date"]


def test_big_auto_field():
    # Primary keys are optional fields when include = __all__
    class ModelBigAuto(models.Model):
        big_auto_filed = models.BigAutoField(primary_key=True)

        class Meta:
            app_label = "tests"

    class ModelBigAutoSchema(ModelSchema):
        class Config:
            model = ModelBigAuto

    print(ModelBigAutoSchema.schema())
    assert ModelBigAutoSchema.schema() == {
        "title": "ModelBigAutoSchema",
        "type": "object",
        "properties": {
            "big_auto_filed": {
                "title": "Big Auto Filed",
                "type": "integer",
                "extra": {},
            }
        },
    }


@pytest.mark.skipif(
    django.VERSION < (3, 1), reason="json field introduced in django 3.1"
)
def test_django_31_fields():
    class ModelNewFields(models.Model):
        json_field = models.JSONField()
        positive_big_integer_field = models.PositiveBigIntegerField()

        class Meta:
            app_label = "tests"

    class ModelNewFieldsSchema(ModelSchema):
        class Config:
            model = ModelNewFields

    print(ModelNewFieldsSchema.schema())
    assert ModelNewFieldsSchema.schema() == {
        "title": "ModelNewFieldsSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer", "extra": {}},
            "json_field": {
                "title": "Json Field",
                "format": "json-string",
                "type": "string",
            },
            "positive_big_integer_field": {
                "title": "Positive Big Integer Field",
                "type": "integer",
            },
        },
        "required": ["json_field", "positive_big_integer_field"],
    }
    with pytest.raises(Exception):
        ModelNewFieldsSchema(
            id=1, json_field={"any": "data"}, positive_big_integer_field=1
        )

    obj = ModelNewFieldsSchema(
        id=1, json_field=json.dumps({"any": "data"}), positive_big_integer_field=1
    )
    assert obj.dict() == {
        "id": 1,
        "json_field": {"any": "data"},
        "positive_big_integer_field": 1,
    }


def test_relational():
    class Related(models.Model):
        char_field = models.CharField()

        class Meta:
            app_label = "tests"

    class TestModel(models.Model):
        many_to_many_field = models.ManyToManyField(Related)
        one_to_one_field = models.OneToOneField(Related, on_delete=models.CASCADE)
        foreign_key = models.ForeignKey(Related, on_delete=models.SET_NULL, null=True)

        class Meta:
            app_label = "tests"

    class TestSchema(ModelSchema):
        class Config:
            model = TestModel

    assert TestSchema.schema() == {
        "title": "TestSchema",
        "type": "object",
        "properties": {
            "id": {"extra": {}, "title": "Id", "type": "integer"},
            "one_to_one_field_id": {"title": "One To One Field", "type": "integer"},
            "foreign_key_id": {"title": "Foreign Key", "type": "integer"},
            "many_to_many_field": {
                "title": "Many To Many Field",
                "type": "array",
                "items": {"type": "integer"},
            },
        },
        "required": ["one_to_one_field_id", "many_to_many_field"],
    }


def test_default():
    class MyModel(models.Model):
        default_static = models.CharField(default="hello")
        default_dynamic = models.CharField(default=lambda: "world")

        class Meta:
            app_label = "tests"

    class MyModelSchema(ModelSchema):
        class Config:
            model = MyModel

    assert MyModelSchema.schema() == {
        "title": "MyModelSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "extra": {}, "type": "integer"},
            "default_static": {
                "title": "Default Static",
                "default": "hello",
                "type": "string",
            },
            "default_dynamic": {"title": "Default Dynamic", "type": "string"},
        },
    }


def test_many_to_many():
    class Movie(models.Model):
        name = models.CharField()

        class Meta:
            app_label = "tests"

    class Character(models.Model):
        many_to_many = models.ManyToManyField(Movie, blank=True)

        class Meta:
            app_label = "tests"

    class CharacterSchema(ModelSchema):
        class Config:
            model = Character

    # Mock database data:
    movie = Mock()
    movie.pk = 1
    movie.name = "test"

    many_to_many = Mock(spec=Manager)
    many_to_many.all = lambda: [movie]

    character = Mock()
    character.id = 1
    character.many_to_many = many_to_many

    data = CharacterSchema.from_orm(character).dict()

    assert data == {"id": 1, "many_to_many": [1]}
