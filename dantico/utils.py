import inspect
import logging
from typing import Any, Dict, Type

from dantico.exceptions import ConfigError
from django.db import models
from django.db.models import Model
from pydantic.utils import is_valid_field

# __all__ = ["compute_field_annotations"]

logger = logging.getLogger()


def compute_field_annotations(
    namespace: "Dict[str, Any]",
    **field_definitions: Any,
) -> "Dict[str, Any]":

    fields = {}
    annotations = {}

    for field_name, field_definition in field_definitions.items():
        if not is_valid_field(field_name):
            logger.debug(
                f'fields may not start with an underscore, ignoring "{field_name}"'
            )
        if isinstance(field_definition, tuple):
            try:
                field_annotation, field_value = field_definition
            except ValueError as e:  # pragma: no cover
                # really?
                # `field_definition` is always a tuple with two elements
                raise ConfigError(
                    "field definitions should either be a tuple of (<type>, <default>) or just a "
                    "default value, unfortunately this means tuples as "
                    "default values are not allowed"
                ) from e
        else:
            # really?
            # `field_definition` is always a tuple with two elements
            field_annotation, field_value = None, field_definition  # pragma: no cover

        if field_annotation:
            annotations[field_name] = field_annotation
        fields[field_name] = field_value

    namespace.update(**{"__annotations__": annotations})
    namespace.update(fields)

    return namespace


def is_valid_django_model(model: Type[Model]) -> bool:
    return is_valid_class(model) and issubclass(model, models.Model)


def is_valid_class(object: type) -> bool:
    return inspect.isclass(object)
