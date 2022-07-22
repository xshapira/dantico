from typing import List
from unittest.mock import Mock

from dantico import Schema
from django.db.models import Manager, QuerySet
from django.db.models.fields.files import ImageFieldFile
from pydantic import Field


class FakeManager(Manager):
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def __str__(self):
        return "FakeManager"


class FakeQS(QuerySet):
    def __init__(self, items):
        self._result_cache = items
        self._prefetch_related_lookups = False

    def __str__(self):
        return "FakeQS"


class Tag:
    def __init__(self, id, title):
        self.id = id
        self.title = title


# Mock user data:
class User:
    name = "Jane"
    group_set = FakeManager([1, 2, 3])
    avatar = ImageFieldFile(None, Mock(), name=None)

    @property
    def tags(self):
        return FakeQS([Tag(1, "foo"), Tag(2, "bar")])


class TagSchema(Schema):
    id: str
    title: str


class UserSchema(Schema):
    name: str
    groups: List[int] = Field(..., alias="group_set")
    tags: List[TagSchema]
    avatar: str = None


def test_schema():
    user = User()
    schema = UserSchema.from_orm(user)
    assert schema.dict() == {
        "name": "Jane",
        "groups": [1, 2, 3],
        "tags": [{"id": "1", "title": "foo"}, {"id": "2", "title": "bar"}],
        "avatar": None,
    }


def test_schema_with_image():
    user = User()
    field = Mock()
    field.storage.url = Mock(return_value="/avatar.jpg")
    user.avatar = ImageFieldFile(None, field, name="avatar.jpg")
    schema = UserSchema.from_orm(user)
    assert schema.dict() == {
        "name": "Jane",
        "groups": [1, 2, 3],
        "tags": [{"id": "1", "title": "foo"}, {"id": "2", "title": "bar"}],
        "avatar": "/avatar.jpg",
    }
