import json
from typing import Any, Literal, Self
from pydantic import BaseModel, Field, RootModel, model_validator
from pydantic_extra_types.language_code import LanguageAlpha2

ID = str

class Translations(BaseModel):
    languages: dict[LanguageAlpha2, str]
    default: LanguageAlpha2

    @model_validator(mode="after")
    def check_default_exists(self) -> Self:
        if self.default not in self.languages:
            raise ValueError(f"Default language '{self.default}' does not exist")
        return self

class BaseComponent(BaseModel):
    id: ID
    label: Translations
    optional: bool = False

class Participant(BaseComponent):
    participant_id: int

class Human(Participant):
    type: Literal["human"]
    user_id: str

class Agent(Participant):
    type: Literal["agent"]
    endpoint: str
    api_key: str
    prompt: str

class Chat(BaseComponent):
    type: Literal["chat"]
    label: str
    participants: list[Participant]
    # 
    order: list[ID] | None

class Choice(BaseComponent):
    choices: list[Translations]
    shuffle: bool = Field(default=False, description="If `true`, choices are displayed in a random order to the user")

class SingleChoice(Choice):
    type: Literal["single_choice"]

class MultiChoice(Choice):
    type: Literal["multi_choice"]


class Slider(BaseComponent):
    type: Literal["slider"]
    steps: int = Field(ge=1)
    labels: list[Translations] | None = None

    @model_validator(mode="after")
    def validate_labels(self) -> Self:
        if self.labels is None:
            self.labels = [Translations(languages={"en": str(i)}, default="en") for i in range(self.steps)]
        if len(self.labels) > 0 and len(self.labels) != self.steps:
            raise ValueError(f"Number of labels ({self.labels}) must equal number of steps ({self.steps})")
        return self


class FreeText(BaseComponent):
    type: Literal["free_text"]
    regex: str | None = Field(default=None, description="The regular expression pattern that the user's input must match. `null` performs no matching.")

ComponentType = SingleChoice | MultiChoice | Slider | FreeText

class ComponentGroup(BaseModel):
    label: Translations | None = None
    components: list[ComponentType]

class TaskPage(BaseModel):
    label: Translations | None = None
    component_groups: list[ComponentGroup] = []
    columns: int = Field(default=1, description="The number of columns used to display the component groups")

class ConstraintAction:
    next_page: str | None = None # None means go to next page

class Constraint:
    condition: list[dict[str, Any]] = []
    action: ConstraintAction = ConstraintAction()

class TaskConfig(BaseModel):
    id: str
    name: Translations
    description: Translations | None = None
    pages: list[TaskPage]
    # constraints: list[Constraint]

    @model_validator(mode='after')
    def check_ids_unique(self) -> Self:
        ids = set()
        for page in self.pages:
            for group in page.component_groups:
                for component in group.components:
                    if component.id in ids:
                        raise ValueError(f"Every component must have a unique ID, duplicated ID: {component.id}")
                    ids.add(component.id)
        return self

print(json.dumps(TaskConfig.model_json_schema(), indent=2))
# test()