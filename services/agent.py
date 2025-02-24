import json

from openai import OpenAI

from settings import settings


class BaseAgent:
    async def get_response(self) -> None: ...


class Agent:
    def __init__(self):
        self.model_name = ""
        self.model = ""
        self.agent_type = ""
        self.messages = []

    def set_attributes(self, model_name, agent_type, language, user_personality):
        self.model_name = model_name
        self.model = OpenAI(base_url=settings.api_url, api_key=settings.api_key)
        self.agent_type = agent_type
        self.user_personality = user_personality

        self.pt_template = open(
            f"services/data/prompts/{language}/LLM_{agent_type}.md", encoding="utf-8"
        ).read()
        self.lang = language

    def set_task(self, task):
        self.task = task

    def fill_prompt(self):
        self.prompt = self.pt_template.format(
            query=self.task.desc[self.lang],
            options=self.task.parse_options(),
            best_choice=self.task.best_choice,
            hidden_incentive=self.task.hidden_incentive,
            personality=self.user_personality,
        )
        self.messages.append({"role": "system", "content": self.prompt})

    def set_prompt(self, prompt):
        self.messages = []
        self.prompt = prompt
        self.messages.append({"role": "system", "content": self.prompt})

    def add_message(self, msg):
        self.messages.append(msg)

    def generate(self, msg):
        res = ""
        self.add_message(msg)
        while True:
            try:
                chat = self.model.chat.completions.create(
                    model=self.model_name, messages=self.messages
                )
                res = chat.choices[0].message.content
                response = {"role": "assistant", "content": res}
                res = json.loads(res)
                self.add_message(response)
                res = {"role": "assistant", "content": res}
                # res = {"role": "assistant", "content": res}
                break
            except Exception:
                ...
        return res

    def empty_messages(self):
        self.messages = []
