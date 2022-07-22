from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    Union,
    cast,
    no_type_check,
)

from dantico.exceptions import ConfigError
from dantico.fields import django_to_pydantic_with_choices
from dantico.utils import compute_field_annotations
from django.db.models import Field, ManyToManyRel, ManyToOneRel
from pydantic import BaseConfig, BaseModel, PyObject
from pydantic.class_validators import (
    extract_root_validators,
    extract_validators,
    inherit_validators,
)
from pydantic.fields import FieldInfo, ModelField, Undefined
from pydantic.main import (
    ANNOTATED_FIELD_UNTOUCHED_TYPES,
    UNTOUCHED_TYPES,
    ModelMetaclass,
    generate_hash_function,
    validate_custom_root_type,
)
from pydantic.typing import get_args, get_origin, is_classvar, resolve_annotations
from pydantic.utils import (
    ROOT_KEY,
    ClassAttribute,
    generate_model_signature,
    is_valid_field,
    lenient_issubclass,
    unique_list,
    validate_field_name,
)

from .getters import DjangoGetter
from .mixins import SchemaMixins
from .model_validators import ModelValidatorGroup
from .schema_registry import registry as global_registry

if TYPE_CHECKING:
    from pydantic.class_validators import ValidatorListDict

ALL_FIELDS = "__all__"

__all__ = ["ModelSchema"]


namespace_keys = [
    "__config__",
    "__fields__",
    "__validators__",
    "__pre_root_validators__",
    "__post_root_validators__",
    "__schema_cache__",
    "__json_encoder__",
    "__custom_root_type__",
    "__private_attributes__",
    "__slots__",
    "__hash__",
    "__class_vars__",
    "__annotations__",
]


class PydanticNamespace:
    __annotations__: Dict = dict()
    __config__: Optional[Type[BaseConfig]] = None
    __fields__: Dict[str, ModelField] = dict()
    __validators__: ModelValidatorGroup = ModelValidatorGroup({})
    __pre_root_validators__: List = []
    __post_root_validators__: List = []
    __custom_root_type__ = None
    __private_attributes__ = None
    __class_vars__: Set = set()

    def __init__(self, cls: Type):
        for key in namespace_keys:
            value = getattr(cls, key, getattr(self, key, None))
            setattr(self, key, value)


def update_class_missing_fields(
    cls: Type, bases: List[Type[BaseModel]], namespace: Dict
) -> Type[BaseModel]:
    old_namespace: PydanticNamespace = PydanticNamespace(cls)
    fields = old_namespace.__fields__ or {}
    config: Type[BaseConfig] = cast(Type[BaseConfig], old_namespace.__config__)
    validators: "ValidatorListDict" = {}

    pre_root_validators, post_root_validators = [], []
    class_vars: Set[str] = set()
    hash_func: Optional[Callable[[Any], int]] = None
    untouched_types = ANNOTATED_FIELD_UNTOUCHED_TYPES

    def is_untouched(val: Any) -> bool:
        return (
            isinstance(val, untouched_types)
            or val.__class__.__name__ == "python_function_or_method"
        )

    for base in reversed(bases):
        if base != BaseModel:
            validators = inherit_validators(base.__validators__, validators)  # type: ignore
            pre_root_validators += base.__pre_root_validators__
            post_root_validators += base.__post_root_validators__
            class_vars.update(base.__class_vars__)
            hash_func = base.__hash__

    validators = inherit_validators(extract_validators(namespace), validators)
    vg = ModelValidatorGroup(validators)
    new_annotations = resolve_annotations(
        namespace.get("__annotations__") or {}, getattr(cls, "__module__", None)
    )
    # Annotation only fields need to come first in fields.
    for ann_name, ann_type in new_annotations.items():
        if is_classvar(ann_type):
            class_vars.add(ann_name)
        elif is_valid_field(ann_name):
            validate_field_name(bases, ann_name)
            value = namespace.get(ann_name, Undefined)
            allowed_types = (
                get_args(ann_type) if get_origin(ann_type) is Union else (ann_type,)  # type: ignore [comparison-overlap]
            )
            if (
                is_untouched(value)
                and ann_type != PyObject
                and not any(
                    lenient_issubclass(get_origin(allowed_type), Type)  # type: ignore
                    for allowed_type in allowed_types
                )
            ):
                continue
            fields[ann_name] = ModelField.infer(
                name=ann_name,
                value=value,
                annotation=ann_type,
                class_validators=vg.get_validators(ann_name),
                config=config,
            )

    untouched_types = UNTOUCHED_TYPES + config.keep_untouched
    for var_name, value in namespace.items():
        can_be_changed = var_name not in class_vars and not is_untouched(value)
        if (
            is_valid_field(var_name)
            and var_name not in new_annotations
            and can_be_changed
        ):
            validate_field_name(bases, var_name)
            inferred = ModelField.infer(
                name=var_name,
                value=value,
                annotation=new_annotations.get(var_name, Undefined),
                class_validators=vg.get_validators(var_name),
                config=config,
            )
            if var_name in fields and inferred.type_ != fields[var_name].type_:
                raise TypeError(
                    f"The type of {cls.__name__}.{var_name} differs from the new default value; "
                    f"if you wish to change the type of this field, please use a type annotation"
                )
            fields[var_name] = inferred

    _custom_root_type = ROOT_KEY in fields
    if _custom_root_type:
        validate_custom_root_type(fields)
    vg.check_for_unused()

    old_namespace.__annotations__.update(new_annotations)
    pre_rv_new, post_rv_new = extract_root_validators(namespace)

    if hash_func is None:
        hash_func = generate_hash_function(config.frozen)
    pre_root_validators.extend(pre_rv_new)
    post_root_validators.extend(post_rv_new)

    new_namespace = {
        "__annotations__": old_namespace.__annotations__,
        "__config__": config,
        "__fields__": fields,
        "__validators__": vg.validators,
        "__pre_root_validators__": unique_list(pre_root_validators),
        "__post_root_validators__": unique_list(post_root_validators),
        "__class_vars__": class_vars,
        "__hash__": hash_func,
    }
    for k, v in new_namespace.items():
        if hasattr(cls, k):
            setattr(cls, k, v)
    # Set __signature__ attr only for model class, but not for its instances.
    cls.__signature__ = ClassAttribute(
        "__signature__", generate_model_signature(cls.__init__, fields, config)
    )
    return cls


class ModelSchemaConfig(BaseConfig):
    def __init__(
        self, schema_class_name: str, options: Optional[Dict[str, Any]] = None
    ):
        super(ModelSchemaConfig, self).__init__()
        self.model = getattr(options, "model", None)
        _include = getattr(options, "include", None) or ALL_FIELDS
        self.include = set() if _include == ALL_FIELDS else set(_include or ())
        self.exclude = set(getattr(options, "exclude", None) or ())
        self.skip_registry = getattr(options, "skip_registry", False)
        self.registry = getattr(options, "registry", global_registry)
        _optional = getattr(options, "optional", None)
        self.optional = (
            {ALL_FIELDS} if _optional == ALL_FIELDS else set(_optional or ())
        )
        self.depth = int(getattr(options, "depth", 0))
        self.schema_class_name = schema_class_name
        self.validate_configuration()
        self.process_build_schema_parameters()

    @classmethod
    def clone_field(cls, field: FieldInfo, **kwargs: Any) -> FieldInfo:
        field_dict = dict(field.__repr_args__())
        field_dict.update(**kwargs)
        new_field = FieldInfo(**field_dict)  # type: ignore
        return new_field

    def model_fields(self) -> Iterator[Field]:
        """Return iterator with all the fields that can be part of a schema."""
        for fld in self.model._meta.get_fields():  # type: ignore
            if isinstance(fld, (ManyToOneRel, ManyToManyRel)):
                # Skipping relations.
                continue
            yield cast(Field, fld)

    def validate_configuration(self) -> None:
        self.include = set() if self.include == ALL_FIELDS else set(self.include or ())  # type: ignore [comparison-overlap]

        if not self.model:
            raise ConfigError("Invalid Configuration. 'model' is required")

        if self.include and self.exclude:
            raise ConfigError(
                "Only one of 'include' or 'exclude' should be set in configuration."
            )

    def check_invalid_keys(self, **field_names: Dict[str, Any]) -> None:
        keys = field_names.keys()
        invalid_include_exclude_fields = (
            set(self.include or []) | set(self.exclude or [])
        ) - keys
        if invalid_include_exclude_fields:
            raise ConfigError(
                f"Field(s) {invalid_include_exclude_fields} are not in model."
            )
        if ALL_FIELDS not in self.optional:
            invalid_options_fields = set(self.optional) - keys
            if invalid_options_fields:
                raise ConfigError(
                    f"Field(s) {invalid_options_fields} are not in model."
                )

    def is_field_in_optional(self, field_name: str) -> bool:
        if not self.optional:
            return False
        if ALL_FIELDS in self.optional:
            return True
        if (
            isinstance(self.optional, (set, tuple, list))
            and field_name in self.optional
        ):
            return True
        return False

    def process_build_schema_parameters(self) -> None:
        model_pk = getattr(
            self.model._meta.pk,  # type: ignore
            "name",
            getattr(self.model._meta.pk, "attname"),  # type: ignore
        )  # no type:ignore
        if (
            model_pk not in self.include
            and model_pk not in self.exclude
            and ALL_FIELDS not in self.optional
        ):
            self.optional.add(str(model_pk))


class ModelSchemaMetaclass(ModelMetaclass):
    @no_type_check
    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: dict,
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases == (SchemaBaseModel,) or not namespace.get("Config"):
            return cls

        if issubclass(cls, ModelSchema):
            config = namespace["Config"]
            config_instance = ModelSchemaConfig(name, config)
            annotations = namespace.get("__annotations__", {})

            try:
                fields = list(config_instance.model_fields())
            except AttributeError as exc:
                raise ConfigError(
                    f"{exc} (Is `Config.model` a valid Django model class?)"
                )

            field_values, _seen = {}, set()

            all_fields = {f.name: f for f in fields}
            config_instance.check_invalid_keys(**all_fields)

            for field in chain(fields, annotations.copy()):
                field_name = getattr(
                    field, "name", getattr(field, "related_name", field)
                )

                if (
                    field_name in _seen
                    or (
                        (
                            config_instance.include
                            and field_name not in config_instance.include
                        )
                        or (
                            config_instance.exclude
                            and field_name in config_instance.exclude
                        )
                    )
                    and field_name not in annotations
                ):
                    continue

                _seen.add(field_name)
                if field_name in annotations and field_name in namespace:

                    python_type = annotations.pop(field_name)
                    pydantic_field = namespace[field_name]
                    if (
                        hasattr(pydantic_field, "default_factory")
                        and pydantic_field.default_factory
                    ):
                        pydantic_field = pydantic_field.default_factory()

                elif field_name in annotations:
                    python_type = annotations.pop(field_name)
                    pydantic_field = (
                        None if Optional[python_type] == python_type else Ellipsis
                    )

                else:
                    python_type, pydantic_field = django_to_pydantic_with_choices(
                        field,
                        registry=config_instance.registry,
                        depth=config_instance.depth,
                        skip_registry=config_instance.skip_registry,
                    )
                    if config_instance.is_field_in_optional(field_name):
                        pydantic_field = ModelSchemaConfig.clone_field(
                            field=pydantic_field, default=None, default_factory=None
                        )

                field_values[field_name] = (python_type, pydantic_field)
            cls = update_class_missing_fields(
                cls, list(bases), compute_field_annotations(namespace, **field_values)
            )
            return cls
        return cls


class SchemaBaseModel(BaseModel, SchemaMixins):
    pass


class ModelSchema(SchemaBaseModel, metaclass=ModelSchemaMetaclass):
    class Config:
        orm_mode = True
        getter_dict = DjangoGetter
        # `ModelSchema` is a `SchemaBaseModel` that uses
        # the `ModelSchemaMetaclass` to generate a schema.
        # We use the `DjangoGetter` to get the values for the fields.
