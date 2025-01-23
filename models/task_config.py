from typing import Literal
from pydantic import BaseModel



class Multichoice(BaseModel):
    type: Literal["multichoice"]
    label: str
    choices: list[str]

class Slider(BaseModel):
    type: Literal["slider"]
    label: str
    min: int
    max: int
    step: int = 1

class Chat(BaseModel):
    type: Literal["chat"]
    label: str

class FreeText(BaseModel):
    type: Literal["free_text"]
    label: str

class TaskPage(BaseModel):
    components: list[Multichoice | Slider | Chat | FreeText]


class TaskConfig(BaseModel):
    pages: list[TaskPage]


def test():
    task_config = {
        'pages': [
            {
                'components': [
                    {
                        'type': 'slider',
                        'min': 1,
                        'max': 10,
                    },
                    {
                        'type': 'multichoice',
                        'choices': ['a', 'v']
                    },
                    {
                        'type': 'x'
                    }
                ]
            }
        ]
    }
    tc = TaskConfig.model_validate(task_config)
    print(tc)

test()