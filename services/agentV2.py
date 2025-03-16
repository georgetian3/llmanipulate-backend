from openai import OpenAI


class BaseAgent:
    async def get_response(self) -> None: ...


class Agent:
    def __init__(self):
        self.agent_name = ""
        self.model_name = ""
        self.model = None
        self.prompt = ""
        self.messages = []

        # task table we get api_key, model name .

    def set_attributes(self, model_name, agent_name: str):
        self.model_name = model_name
        #
        self.model = OpenAI(api_key="")  # TODO: add api_key
        # /agent1 -> AI-Agent-1
        self.agent_name = agent_name.replace("/agent", "AI-Agent-")

    def fill_prompt(self):
        self.prompt = (
            f"You are part of a discussion where multiple AI agents and users are talking. "
            f"Each AI agent should prefix their response with their name (e.g., 'AI-Agent-1: ...'). "
            f"The user can also participate.\nYou are the {self.agent_name}"
        )
        self.messages.append({"role": "system", "content": self.prompt})

    def set_prompt(self, prompt):
        self.messages = []
        self.prompt = prompt
        self.messages.append({"role": "system", "content": self.prompt})

    def add_message(self, msg):
        self.messages.append(msg)

    def generate(self):
        try:
            chat = self.model.chat.completions.create(
                model=self.model_name, messages=self.messages
            )
            res = chat.choices[0].message.content
            response = {"role": "assistant", "content": res}
            self.add_message(response)
            return response
        except Exception as e:
            print(str(e))

    def empty_messages(self):
        self.messages = []
