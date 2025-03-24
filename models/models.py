from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def to_model(from_class_instance: BaseModel, to_class: Type[T]) -> T:
    return to_class(**from_class_instance.model_dump())