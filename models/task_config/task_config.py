from collections.abc import Generator
from functools import cached_property
from typing import Any, Self

from pydantic import BaseModel, Field, model_validator

from models.task_config.base_component import Translations
from models.task_config.components import ComponentType


class ColumnsMixin(BaseModel):
    columns: int = Field(
        default=1,
        description="The number of columns used to display the children of this component",
    )


class ComponentGroup(ColumnsMixin):
    label: Translations | None = None
    components: list[ComponentType]


class TaskPage(ColumnsMixin):
    label: Translations | str | None = None
    component_groups: list[ComponentGroup]
    columns: int = Field(
        default=1,
        description="The number of columns used to display the component groups",
    )


class TaskConfig(BaseModel):
    name: Translations
    description: Translations | None = None
    pages: list[TaskPage]
    public: bool

    @model_validator(mode="after")
    def check_ids_unique(self) -> Self:
        ids = set()
        for component in self.components:
            if component.id in ids:
                raise ValueError(f"Duplicate component ID: {component.id}")
            ids.add(component.id)
        return self

    @property
    def components(self) -> Generator[ComponentType, None, None]:
        for page in self.pages:
            for group in page.component_groups:
                for component in group.components:
                    yield component

    @cached_property
    def component_map(self) -> dict[str, ComponentType]:
        map = {}
        for component in self.components:
            map[component.id] = component
        return map