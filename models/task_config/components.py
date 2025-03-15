import re
from typing import Literal, Self

from pydantic import Field, RootModel, model_validator

from models.task_config.base_component import BaseComponent, Translations
from models.task_config.chat import Chat
from models.task_config.responses import (
    ComponentResponseType,
    IntResponseType,
    ListIntResponseType,
    StringResponseType,
)


class Choice(BaseComponent):
    choices: list[Translations]
    shuffle: bool = Field(
        default=False,
        description="If `true`, choices are displayed in a random order to the user",
    )


class SingleChoice(Choice):
    type: Literal["single_choice"] = "single_choice"
    response_class = IntResponseType

    def validate_response(self, response):
        super().validate_response(response)
        if not 0 <= response.root < len(self.choices):
            raise ValueError(f"Choice must be in range [0, {len(self.choices)})")


class MultiChoice(Choice):
    type: Literal["multi_choice"] = "multi_choice"
    response_class = ListIntResponseType
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

    def validate_response(self, response: ComponentResponseType):
        super().validate_response(response)
        if len(set(response.root)) != len(response.root):
            raise ValueError("Response cannot contain duplicates")
        if not self.min_choices <= len(response.root) <= self.max_choices:
            raise ValueError(
                f"Number of choices must be in range [{self.min_choices}, {len(self.max_choices)}]"
            )
        for choice in response.root:
            if not 0 <= choice < len(self.choices):
                raise ValueError(f"Choice must be in range [0, {len(self.choices)}]")


class Slider(BaseComponent):
    type: Literal["slider"] = "slider"
    steps: int = Field(ge=1)
    labels: list[Translations] | None = None
    response_class = IntResponseType

    @model_validator(mode="after")
    def validate_labels(self) -> Self:
        if self.labels is None:
            self.labels = [
                Translations(languages={"en": str(i)}) for i in range(self.steps)
            ]
        if len(self.labels) > 0 and len(self.labels) != self.steps:
            raise ValueError(
                f"Number of labels ({self.labels}) must equal number of steps ({self.steps})"
            )
        return self

    def validate_response(self, response):
        super().validate_response(response)
        if not 0 <= response.root < self.steps:
            raise ValueError(f"Slider value must be in range [0, {self.steps}]")


class FreeText(BaseComponent):
    type: Literal["free_text"] = "free_text"
    regex: str | None = Field(
        None,
        description="The regular expression pattern that the user's input must match. `null` performs no matching.",
    )
    regex_prompt: str | None = Field(
        None, description="Prompt to be shown if the regex does not match"
    )
    response_class = StringResponseType

    def validate_response(self, response):
        super().validate_response(response)
        if self.regex and not re.search(self.regex, response.root):
            raise ValueError("Text input does not satisfy regex")


ComponentType = SingleChoice | MultiChoice | Slider | FreeText | Chat
