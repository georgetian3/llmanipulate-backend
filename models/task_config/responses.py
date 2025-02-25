from pydantic import RootModel


class SingleChoiceResponse(RootModel[int]): ...


class MultiChoiceResponse(RootModel[list[int]]): ...


class SliderResponse(RootModel[int]): ...


class FreeTextResponse(RootModel[str]): ...


ComponentResponseType = (
    SingleChoiceResponse | MultiChoiceResponse | SliderResponse | FreeTextResponse
)
