import json
from typing import Any, Literal, Self
from pydantic import BaseModel, Field, RootModel, model_validator
from pydantic_extra_types.language_code import LanguageAlpha2

ID = str

class Translations(BaseModel):
    languages: dict[LanguageAlpha2, str] = Field(examples=[{"en": "This is the english translation.", "zh": "这是中文翻译。"}])
    default: LanguageAlpha2 | None = Field(
        default=None, examples=["en", "zh"],
        description="Default language to display. Must must be in `languages`. Will display an arbitrary language if left `null`."
    )

    @model_validator(mode="after")
    def check_default_exists(self) -> Self:
        if len(self.languages) > 1 and self.default not in self.languages:
            raise ValueError(f"Default language '{self.default}' does not exist")
        return self

class ColumnsMixin(BaseModel):
    columns: int = Field(default=1, description="The number of columns used to display the children of this component")

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
    type: Literal["single_choice"] = "single_choice"

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
            raise ValueError(f"The inequality 0 <= min_choices <= max_choices <= len(choices) must be satisfied for component {self.id}")
        return self


class Slider(BaseComponent):
    type: Literal["slider"] = "slider"
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
    type: Literal["free_text"] = "free_text"
    regex: str | None = Field(default=None, description="The regular expression pattern that the user's input must match. `null` performs no matching.")

class ComponentGroup(ColumnsMixin):
    label: Translations | None = None
    components: list[SingleChoice | MultiChoice | Slider | FreeText]

class TaskPage(ColumnsMixin):
    label: Translations | None = None
    component_groups: list[ComponentGroup]
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

sample_task_config = TaskConfig(
    id="test config",
    name=Translations(
        languages={"en": "test name", "zh": "测试名字"},
        default="en"
    ),
    description=Translations(languages={"en": "test", "zh": "测试描述"}, default="zh"),
    pages=[
        TaskPage(
            label=Translations(languages={"en": "page label"}),
            component_groups=[
                ComponentGroup(
                    label=Translations(languages={"en": "Component group label"}),
                    columns=2,
                    components=[
                        Slider(
                            id="s1",
                            steps=3,
                            label=Translations(languages={"en": "Slider", "zh": "滑动"}, default="en"),
                            labels=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                        ),
                        SingleChoice(
                            id="sc1",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                            label=Translations(languages={"en": "Single Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc1",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                            label=Translations(languages={"en": "Multi Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f1",
                            label=Translations(languages={"en": "Free text", "zh": "滑动"}, default="en"),
                            regex=".*f.*"
                        )
                    ]
                )
            ]
        ),
        TaskPage(
            label=Translations(languages={"en": "page label"}),
            component_groups=[
                ComponentGroup(
                    label=Translations(languages={"en": "Component group label"}),
                    columns=2,
                    components=[
                        Slider(
                            id="s2",
                            label=Translations(languages={"en": "Slider", "zh": "滑动"}, default="en"),
                            steps=3,
                            labels=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                        ),
                        SingleChoice(
                            id="sc2",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                            label=Translations(languages={"en": "Single Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc2",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                            label=Translations(languages={"en": "Multi Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f2",
                            label=Translations(languages={"en": "Free text", "zh": "滑动"}, default="en"),
                            regex=".*f.*"
                        )
                    ]
                )
            ]
        )
    ]
)