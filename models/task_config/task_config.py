from collections.abc import Generator
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


class ConstraintAction:
    next_page: str | None = None  # None means go to next page


class Constraint:
    condition: list[dict[str, Any]] = []
    action: ConstraintAction = ConstraintAction()


class TaskConfig(BaseModel):
    name: Translations
    description: Translations | None = None
    # use default factory so that field generated as non-null in typescript
    pages: list[TaskPage]
    # constraints: list[Constraint]

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
