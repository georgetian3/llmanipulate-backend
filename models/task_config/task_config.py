from datetime import UTC, datetime
from typing import Any, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from models.task_config.base_component import BaseComponent, Translations
from models.task_config.chat import Chat


class Choice(BaseComponent):
    choices: list[Translations]
    shuffle: bool = Field(
        default=False,
        description="If `true`, choices are displayed in a random order to the user",
    )


class SingleChoice(Choice):
    type: Literal["single_choice"] = "single_choice"


class SingleChoiceResponse(int): ...


class MultiChoice(Choice):
    type: Literal["multi_choice"] = "multi_choice"
    min_choices: int = 0
    max_choices: int = 99999

    @model_validator(mode="after")
    def validate_choices(self) -> Self:
        if self.min_choices < 0:
            self.min_choices = 0
        if self.max_choices > len(self.choices):
            self.max_choices = len(self.choices)
        if not (0 <= self.min_choices <= self.max_choices <= len(self.choices)):
            raise ValueError(
                f"The inequality 0 <= min_choices <= max_choices <= len(choices) must be satisfied for component {self.id}"
            )
        return self


class MultiChoiceResponse(list[int]): ...


class Slider(BaseComponent):
    type: Literal["slider"] = "slider"
    steps: int = Field(ge=1)
    labels: list[Translations] | None = None

    @model_validator(mode="after")
    def validate_labels(self) -> Self:
        if self.labels is None:
            self.labels = [
                Translations(languages={"en": str(i)}, default="en")
                for i in range(self.steps)
            ]
        if len(self.labels) > 0 and len(self.labels) != self.steps:
            raise ValueError(
                f"Number of labels ({self.labels}) must equal number of steps ({self.steps})"
            )
        return self


class FreeText(BaseComponent):
    type: Literal["free_text"] = "free_text"
    regex: str | None = Field(
        default=None,
        description="The regular expression pattern that the user's input must match. `null` performs no matching.",
    )


class ColumnsMixin(BaseModel):
    columns: int = Field(
        default=1,
        description="The number of columns used to display the children of this component",
    )


class ComponentGroup(ColumnsMixin):
    label: Translations | None = None
    components: list[SingleChoice | MultiChoice | Slider | FreeText | Chat]


class TaskPage(ColumnsMixin):
    label: Translations | None = None
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
    id: str
    name: Translations
    description: Translations | None = None
    pages: list[TaskPage] = Field(min_length=1)
    # constraints: list[Constraint]

    @model_validator(mode="after")
    def check_ids_unique(self) -> Self:
        ids = set()
        for page in self.pages:
            for group in page.component_groups:
                for component in group.components:
                    if component.id in ids:
                        raise ValueError(
                            f"Every component must have a unique ID, duplicated ID: {component.id}"
                        )
                    ids.add(component.id)
        return self
