from pydantic import RootModel

IntResponseType = RootModel[int]
ListIntResponseType = RootModel[list[int]]
StringResponseType = RootModel[str]

ComponentResponseType = IntResponseType | ListIntResponseType | StringResponseType
