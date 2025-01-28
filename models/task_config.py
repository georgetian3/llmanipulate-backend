from typing import Literal, Self
from pydantic import BaseModel, model_validator


ID = str | int


class BaseComponent(BaseModel):
    id: ID
    label: dict[str, str] # mapping of lang to label
    optional: bool = False

class Description(BaseComponent):
    ...

class Multichoice(BaseComponent):
    type: Literal["multichoice"]
    label: str
    choices: list[str]

class Slider(BaseComponent):
    type: Literal["slider"]
    label: str
    min: int = 1
    max: int = 10
    step: int = 1

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

class FreeText(BaseComponent):
    type: Literal["free_text"]
    label: str = ""

class ComponentGroup(BaseModel):
    label: str = ""
    components: list[BaseComponent]

class TaskPage(BaseModel):
    label: str = ""
    component_groups: list[ComponentGroup]
    rows: int | None = None
    cols: int | None = None

class TaskConfig(BaseModel):
    name: str
    pages: list[TaskPage]
    constraints: list[Constraint]

    @model_validator(mode='after')
    def check_ids_unique(self) -> Self:
        ids = []
        for page in self.pages:
            ids = [*ids, *(component.id for component in page.components)]
        id_set = set(ids)
        if id_set == set([None]):
            return self
        if len(ids) != len(id_set):
            raise ValueError("Each every component in each task must have a unique ID or none at all.")
        return self

def test():
    task_config = {
        'name': 'test task',
        'pages': [
            {
                'components': [
                    {
                        'type': 'slider',
                        'label': 'test slider',
                        'min': 1,
                        'max': 10,
                    },
                    {
                        "id": 1,
                        'type': 'multichoice',
                        'label': 'test mulcichoice',
                        'choices': ['a', 'v']
                    },
                ]
            }
        ]
    }

    response = {
        "a": {
            "choice": 0
        },
        "b": {
            "postiion": 4
        }
    }
    tc = TaskConfig.model_validate(task_config)
    print(tc)

test()