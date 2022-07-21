from typing import Any, Callable, Dict, Type

from django.db.models import Model as DjangoModel


class SchemaMixins:
    dict: Callable

    def apply_to_model(
        self, model_instance: Type[DjangoModel], **kwargs: Dict[str, Any]
    ) -> Type[DjangoModel]:
        for attr, value in self.dict(**kwargs).items():
            setattr(model_instance, attr, value)
        return model_instance
