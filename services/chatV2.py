import json

from models.database import get_session
from models.models import LLMInput, LLMResponse
from models.user import User
from services.agentV2 import Agent
from services.tasks import Task


def config_agent(agent_name: str) -> Agent:
    agent = Agent()
    model_name = "gpt-4o-mini"
    agent.set_attributes(model_name, agent_name)
    agent.fill_prompt()
    return agent
