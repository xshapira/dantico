import datetime
import re
from decimal import Decimal
from enum import Enum
from functools import singledispatch
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    no_type_check,
)
from uuid import UUID

import django
from dantico.factory import SchemaFactory
from dantico.schema_registry import SchemaRegister, registry as global_registry
from django.db import models
from django.db.models.fields import Field
from django.utils.encoding import force_str
from pydantic import AnyUrl, EmailStr, IPvAnyAddress, Json
from pydantic.fields import FieldInfo, Undefined

if TYPE_CHECKING:
    from dantico.model_schema import ModelSchema


TModel = TypeVar("TModel")


NAME_PATTERN = r"^[_a-zA-Z][_a-zA-Z0-9]*$"
COMPILED_NAME_PATTERN = re.compile(NAME_PATTERN)


def is_valid_name(name: str) -> None:
    """Checks that the given choice name for choices is valid."""
    assert COMPILED_NAME_PATTERN.match(
        name
    ), f'Names must match /{NAME_PATTERN}/ but "{name}" does not.'


def choices_name_to_string(name: str) -> str:
    """
    Convert the given Django choices name to a string,
    which is used in the schema for serializing and deserializing model fields that have choices defined on them.
    We do it because when you define a field with an Enum type as its validator, then you can't use strings as values for
    the field's "choices", instead, you must use the Enum's member names.

    :param name:str: Pass in the name of the choice that is being converted to a string
    :return: The name of the choice if it is valid, otherwise it returns a string representation of the choice
    """
    name = force_str(name)
    try:
        is_valid_name(name)
    except AssertionError:
        name = f"A_{name}"
    return name


def get_choices(
    choices: Iterable[Union[Tuple[Any, Any], Tuple[str, Iterable[Tuple[Any, Any]]]]]
) -> Iterator[Tuple[str, str, str]]:
    for value, _options in choices:
        try:
            label, name = _options  # unpack
        except ValueError:
            label, name = _options, None  # unpack

        if name:
            yield from get_choices(choices=[(value, label)])
        else:
            name = choices_name_to_string(value)
            description = force_str(label)
            yield name, value, description


class FieldConversionProps:
    description: str
    blank: bool
    is_null: bool
    max_length: int
    alias: str
    title: str

    def __init__(self, field: Field):
        field_options = field.deconstruct()[3]  # 3 are the keywords
        data = {
            "description": force_str(
                getattr(field, "help_text", field.verbose_name)
            ).strip()
        }

        data["title"] = field.verbose_name.title()
        if not field.is_relation:
            data["blank"] = field_options.get("blank", False)
            data["is_null"] = field_options.get("null", False)
            data["max_length"] = field_options.get("max_length")
            data.update(alias=None)
        if field.is_relation and hasattr(field, "get_attname"):
            data["alias"] = field.get_attname()
        self.__dict__ = data


def django_to_pydantic_with_choices(
    field: Field,
    *,
    registry: SchemaRegister,
    depth: int = 0,
    skip_registry: bool = False,
) -> Tuple[Type, FieldInfo]:
    return django_to_pydantic(
        field, registry=registry, depth=depth, skip_registry=skip_registry
    )


@singledispatch
def django_to_pydantic(
    field: Field, **kwargs: Any
) -> Tuple[Type, FieldInfo]:  # pragma: no cover # an abstract function
    raise Exception(f"Could not infer Django field {field} ({field.__class__})")


@no_type_check
def create_m2m_link_type(type_: Type[TModel]) -> Type[TModel]:
    class M2MLink(type_):  # type: ignore
        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            return v.pk

    return M2MLink


@no_type_check
def construct_related_field_schema(
    field: Field, *, registry: SchemaRegister, depth: int, skip_registry=False
) -> Tuple[Type["ModelSchema"], FieldInfo]:
    # Create a sample config and return the type
    model = field.related_model
    schema = SchemaFactory.create_schema(
        model, depth=depth - 1, registry=registry, skip_registry=skip_registry
    )
    default = ...
    if not field.concrete and field.auto_created or field.null:
        default = None
    if isinstance(field, models.ManyToManyField):
        schema = List[schema]  # type: ignore

    return (
        schema,
        FieldInfo(
            default=default,
            description=force_str(
                getattr(field, "help_text", field.verbose_name)
            ).strip(),
            title=field.verbose_name.title(),
        ),
    )


@no_type_check
def construct_relational_field_info(
    field: Field,
    *,
    registry: SchemaRegister,
    depth: int = 0,
    __module__: str = __name__,
) -> Tuple[Type, FieldInfo]:
    default: Any = ...
    field_props = FieldConversionProps(field)

    inner_type, field_info = django_to_pydantic(
        field.related_model._meta.pk, registry=registry, depth=depth
    )

    if not field.concrete and field.auto_created or field.null:
        default = None

    python_type = inner_type
    if field.one_to_many or field.many_to_many:
        m2m_type = create_m2m_link_type(inner_type)
        python_type = List[m2m_type]  # type: ignore

    field_info = FieldInfo(
        default=default,
        alias=field_props.alias,
        default_factory=None,
        title=field_props.title,
        description=field_props.description,
        max_length=None,
    )
    return python_type, field_info


@no_type_check
def construct_field_info(
    python_type: type,
    field: Field,
    depth: int = 0,
    __module__: str = __name__,
    is_custom_type: bool = False,
) -> Tuple[Type, FieldInfo]:
    default = ...
    default_factory = None

    field_props = FieldConversionProps(field)

    if field.choices:
        choices = list(get_choices(field.choices))
        named_choices = [(c[2], c[1]) for c in choices]
        python_type = Enum(  # type: ignore
            f"{field.name.title().replace('_', '')}Enum",
            named_choices,
            module=__module__,
        )
        is_custom_type = True

    if field.has_default():
        if callable(field.default):
            default_factory = field.default
        elif isinstance(field.default, Enum):
            default = field.default.value
        else:
            default = field.default
    elif field_props.blank or field_props.is_null:
        default = None

    if default_factory:
        default = Undefined

    return (
        python_type,
        FieldInfo(
            default=default,
            alias=field_props.alias,
            default_factory=default_factory,
            title=field_props.title,
            description=field_props.description,
            max_length=None if is_custom_type else field_props.max_length,
        ),
    )


@no_type_check
@django_to_pydantic.register(models.CharField)
@django_to_pydantic.register(models.TextField)
@django_to_pydantic.register(models.SlugField)
@django_to_pydantic.register(models.GenericIPAddressField)
@django_to_pydantic.register(models.FileField)
@django_to_pydantic.register(models.FilePathField)
def field_to_string(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(str, field)


@no_type_check
@django_to_pydantic.register(models.EmailField)
def field_to_email_string(
    field: Field, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(EmailStr, field, is_custom_type=True)


@no_type_check
@django_to_pydantic.register(models.URLField)
def field_to_url_string(
    field: Field, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(AnyUrl, field, is_custom_type=True)


@no_type_check
@django_to_pydantic.register(models.AutoField)
def field_to_id(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(int, field)


@no_type_check
@django_to_pydantic.register(models.UUIDField)
def field_to_uuid(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(UUID, field)


@no_type_check
@django_to_pydantic.register(models.PositiveIntegerField)
@django_to_pydantic.register(models.PositiveSmallIntegerField)
@django_to_pydantic.register(models.SmallIntegerField)
@django_to_pydantic.register(models.BigIntegerField)
@django_to_pydantic.register(models.IntegerField)
def field_to_int(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(int, field)


@no_type_check
@django_to_pydantic.register(models.BinaryField)
def field_to_byte(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(bytes, field)


@no_type_check
@django_to_pydantic.register(models.IPAddressField)
@django_to_pydantic.register(models.GenericIPAddressField)
def field_to_ipaddress(
    field: Field, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(IPvAnyAddress, field)


@no_type_check
@django_to_pydantic.register(models.FloatField)
def field_to_float(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(float, field)


@no_type_check
@django_to_pydantic.register(models.DecimalField)
def field_to_decimal(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(Decimal, field)


@no_type_check
@django_to_pydantic.register(models.BooleanField)
def field_to_boolean(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(bool, field)


@no_type_check
@django_to_pydantic.register(models.NullBooleanField)
def field_to_null_boolean(
    field: Field, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(bool, field)


@no_type_check
@django_to_pydantic.register(models.DurationField)
def field_to_time_delta(
    field: Field, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.timedelta, field)


@no_type_check
@django_to_pydantic.register(models.DateTimeField)
def datetime_to_string(
    field: Field, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.datetime, field)


@no_type_check
@django_to_pydantic.register(models.DateField)
def date_to_string(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.date, field)


@no_type_check
@django_to_pydantic.register(models.TimeField)
def time_to_string(field: Field, **kwargs: Dict[str, Any]) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.time, field)


@no_type_check
@django_to_pydantic.register(models.OneToOneRel)
def one_to_one_field_to_django_model(
    field: Field, registry=None, depth=0, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    return construct_relational_field_info(
        field, registry=registry, depth=depth
    )  # pragma: no cover # not yet implemented


@no_type_check
@django_to_pydantic.register(models.ManyToManyField)
@django_to_pydantic.register(models.ManyToManyRel)
@django_to_pydantic.register(models.ManyToOneRel)
def field_to_list_or_connection(
    field: Field, registry=None, depth=0, skip_registry=False, **kwargs: Dict[str, Any]
) -> Tuple[Type, FieldInfo]:
    if depth > 0:
        return construct_related_field_schema(
            field, depth=depth, registry=registry, skip_registry=skip_registry
        )
    return construct_relational_field_info(field, registry=registry, depth=depth)


@no_type_check
@django_to_pydantic.register(models.OneToOneField)
@django_to_pydantic.register(models.ForeignKey)
def field_to_django_model(
    field: Field,
    registry: Optional[SchemaRegister] = None,
    depth: int = 0,
    skip_registry: bool = False,
    **kwargs: Dict[str, Any],
) -> Tuple[Type, FieldInfo]:
    if depth > 0:
        return construct_related_field_schema(
            field,
            depth=depth,
            registry=registry or global_registry,
            skip_registry=skip_registry,
        )
    return construct_relational_field_info(field, registry=registry, depth=depth)


if django.VERSION >= (3, 1):

    @no_type_check
    @django_to_pydantic.register(models.JSONField)
    def field_to_json_string(
        field: Field, **kwargs: Dict[str, Any]
    ) -> Tuple[Type, FieldInfo]:
        python_type = Json
        if field.null:
            python_type = Optional[Json]
        return construct_field_info(python_type, field)
