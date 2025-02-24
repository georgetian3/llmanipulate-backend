from typing import Self

from pydantic import UUID4, BaseModel, Field, model_validator
from pydantic_extra_types.language_code import LanguageAlpha2

ID = UUID4


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




class BaseComponent(BaseModel):
    id: str | int
    label: Translations | None
    optional: bool = False
