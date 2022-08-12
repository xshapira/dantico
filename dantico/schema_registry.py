from typing import TYPE_CHECKING, Dict, Tuple, Type, Union

from dantico.schema import Schema
from dantico.utils import is_valid_class, is_valid_django_model
from django.db.models import Model

if TYPE_CHECKING:
    from dantico.model_schema import ModelSchema

__all__ = ["SchemaRegister", "registry"]


class SchemaRegisterBorg:
    _shared_state: Dict[str, Dict] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


class SchemaRegister(SchemaRegisterBorg):
    schemas: Dict[Type[Model], Union[Type["ModelSchema"], Type[Schema]]]
    fields: Dict[str, Tuple]

    def __init__(self) -> None:
        SchemaRegisterBorg.__init__(self)
        if not hasattr(self, "schemas"):
            self._shared_state.update(schemas={}, fields={})

    def register_model(self, model: Type[Model], schema: Type["ModelSchema"]) -> None:
        from dantico.model_schema import ModelSchema

        assert is_valid_class(schema) and issubclass(
            schema, (ModelSchema,)
        ), f'Only Schema can be registered, received "{schema.__name__}"'

        assert is_valid_django_model(
            model
        ), f"Only Django Models are allowed. {model.__name__}"

        self.register_schema(model, schema)

    def register_schema(
        self, name: Type[Model], schema: Union[Type["ModelSchema"], Type[Schema]]
    ) -> None:
        self.schemas[name] = schema

    def get_model_schema(
        self, model: Type[Model]
    ) -> Union[Type["ModelSchema"], Type[Schema], None]:
        return self.schemas[model] if model in self.schemas else None


registry = SchemaRegister()
