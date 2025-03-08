from abc import abstractmethod
from typing import ClassVar, Self

from pydantic import BaseModel, Field, RootModel, model_validator
from pydantic_extra_types.language_code import LanguageAlpha2

from models.task_config.responses import ComponentResponseType


class Translations(BaseModel):
    languages: dict[LanguageAlpha2, str] = Field(
        examples=[{"en": "This is the english translation.", "zh": "这是中文翻译。"}]
    )
    default: LanguageAlpha2 | None = Field(
        default=None,
        examples=["en", "zh"],
        description="Default language to display. Must must be in `languages`. Will display an arbitrary language if left `null`.",
    )

    @model_validator(mode="after")
    def check_default_exists(self) -> Self:
        if len(self.languages) > 1 and self.default not in self.languages:
            raise ValueError(f"Default language '{self.default}' does not exist")
        return self


ComponentIdType = str | int


class BaseComponent(BaseModel):
    id: ComponentIdType
    label: Translations | None = None
    optional: bool = False
    response_class: ClassVar[type]

    @abstractmethod
    def validate_response(self, response: ComponentResponseType) -> None:
        if not isinstance(response, self.response_class):
            raise ValueError(f"Response not instance of {self.response_class}")
