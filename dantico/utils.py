import inspect
import logging
from typing import Any, Dict, Tuple, Type

from django.db import models
from django.db.models import Model
from pydantic.fields import FieldInfo
from pydantic.utils import is_valid_field

# __all__ = ["compute_field_annotations"]

logger = logging.getLogger()


def compute_field_annotations(
    namespace: "Dict[str, Any]",
    **field_definitions: Dict[str, Tuple[Type, FieldInfo]],
) -> "Dict[str, Any]":

    fields = {}
    annotations = {}

    for field_name, field_definition in field_definitions.items():
        if not is_valid_field(field_name):
            logger.debug(
                f'fields may not start with an underscore, ignoring "{field_name}"'
            )
        field_annotation, field_value = field_definition

        if field_annotation:
            annotations[field_name] = field_annotation
        fields[field_name] = field_value

    namespace.update(**{"__annotations__": annotations})
    namespace.update(fields)

    return namespace


def is_valid_django_model(model: Type[Model]) -> bool:
    return issubclass(model, models.Model)


def is_valid_class(object: type) -> bool:
    return inspect.isclass(object)
