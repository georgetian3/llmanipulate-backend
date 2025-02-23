from datetime import UTC, datetime
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
    label: Translations | None
    optional: bool = False

class Participant(BaseModel):
    id: ID
    name: str

class Human(Participant):
    type: Literal["human"] = "human"

class Agent(Participant):
    type: Literal["agent"] = "agent"
    endpoint: str
    api_key: str
    prompt: str


class ChatMessage(BaseModel):
    id: ID
    sender: ID
    message: str
    timestamp: datetime

class ChatHistory(BaseModel):
    id: str
    messages: list[ChatMessage]

class Chat(BaseComponent):
    type: Literal["chat"] = "chat"
    label: Translations | None = None
    participants: list[Participant] = []
    order: list[ID] | None = []

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
    components: list[SingleChoice | MultiChoice | Slider | FreeText | Chat]

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
    pages: list[TaskPage] = Field(min_length=1)
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
            label=Translations(languages={"en": "Page title"}),
            columns=1,
            component_groups=[
                ComponentGroup(
                    label=Translations(languages={"en": "Component group 1"}),
                    columns=4,
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
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"}), Translations(languages={"en": "4"})],
                            label=Translations(languages={"en": "Multi Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f1",
                            label=Translations(languages={"en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)", "zh": "滑动"}, default="en"),
                            regex=".*f.*"
                        ),
                    ]
                ),
                ComponentGroup(
                    label=Translations(languages={"en": "Component group 2"}),
                    columns=2,
                    components=[
                        Slider(
                            id="s12",
                            steps=3,
                            label=Translations(languages={"en": "Slider", "zh": "滑动"}, default="en"),
                            labels=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                        ),
                        SingleChoice(
                            id="sc12",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                            label=Translations(languages={"en": "Single Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc12",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"}), Translations(languages={"en": "4"})],
                            label=Translations(languages={"en": "Multi Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f12",
                            label=Translations(languages={"en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)", "zh": "滑动"}, default="en"),
                            regex=".*f.*"
                        ),
                    ]
                ),
                ComponentGroup(
                    label=Translations(languages={"en": "Component group 3"}),
                    columns=1,
                    components=[
                        Slider(
                            id="s13",
                            steps=3,
                            label=Translations(languages={"en": "Slider", "zh": "滑动"}, default="en"),
                            labels=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                        ),
                        SingleChoice(
                            id="sc13",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"})],
                            label=Translations(languages={"en": "Single Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc13",
                            choices=[Translations(languages={"en": "1"}), Translations(languages={"en": "2"}), Translations(languages={"en": "3"}), Translations(languages={"en": "4"})],
                            label=Translations(languages={"en": "Multi Choice", "zh": "滑动"}, default="en"),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f13",
                            label=Translations(languages={"en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)", "zh": "滑动"}, default="en"),
                            regex=".*f.*"
                        ),
                    ]
                )
            ]
        ),
        TaskPage(
            label=Translations(languages={"en": "Page title"}),
            columns=2,
            component_groups=[
                ComponentGroup(
                    columns=1,
                    components=[
                        Chat(
                            id="chat"
                        )
                    ]
                ),
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
                            label=Translations(languages={"en": "Free text *with* **markdown** [test](h)", "zh": "滑动"}, default="en"),
                            regex=".*f.*"
                        ),

                    ]
                )
            ]
        )
    ]
)


sample_chat_history = ChatHistory(
    id="sample chat history",
    messages=[
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 2, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test ",
            timestamp=datetime(2025, 1, 1, 1, 1, 3, tzinfo=UTC),
        ),
        ChatMessage(
            id='2',
            sender='2',
            message="test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test ",
            timestamp=datetime(2025, 1, 1, 1, 1, 4, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            id='2',
            sender='2',
            message="test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test ",
            timestamp=datetime(2025, 1, 1, 1, 1, 4, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='1',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            id='1',
            sender='2',
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
    ]
)