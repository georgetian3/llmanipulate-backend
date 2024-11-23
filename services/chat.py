import asyncio
import json

from models.database import get_session
from sqlalchemy.future import select
from models.models import LLMResponse, LLMInput, User
from services.agent import Agent
from services.task import Task
from services.responses import save_response



async def config_agent(llmp_input: LLMInput):
    agent = Agent()

    model_name = "gpt-3.5-turbo"
    response = {}

    async with get_session() as session:
        query = select(User).where(User.id == llmp_input.user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

    language = user.demographics.get("lang")
    user_personality = user.personality

    task = Task()
    task_type = user.task_type
    task_id = llmp_input.task_id

    tasks = json.loads(open("services/data/tasks.json", "r").read())
    task_by_type = tasks.get(task_type)
    task_by_id = next((task for task in task_by_type if task["task_id"] == task_id), None)

    task.set_attributes(
        _id=task_by_id["task_id"],
        title=task_by_id["query"]["title"],
        desc=task_by_id["query"]["desc"],
        options=task_by_id["options"],
        hidden_incentive=task_by_id["hidden_incentive"],
        lang=language
    )
    agent_type = user.agent_type
    agent.set_attributes(model_name, agent_type, language, user_personality)
    agent.set_task(task)
    agent.fill_prompt()
    return agent


async def get_llm_response(llm_input: LLMInput, agent: Agent, response_id: int) -> LLMResponse:
    msg = {"role": "user", "content": llm_input.message}

    response_content = agent.generate(msg).get("content")
    await save_response(agent, response_id)

    return LLMResponse(response=response_content)



"""

To test  *** 
async def main():
    tasks = json.loads(open("services/data/tasks.json", "r").read())
    print("Hello")
    llm_input = LLMInput(user_id="1", task_id=1, message="Hello")
    agent = await config_agent(llm_input)
    response_id = await create_response(llm_input.user_id, llm_input.task_id)

    response1 = await get_llm_response(llm_input, agent, response_id)
    print(response1)
    print("you tell me")
    llm_input2 = LLMInput(user_id="1", task_id=1, message="you tell me")
    response2 = await get_llm_response(llm_input2, agent, response_id)
    print(response2)

asyncio.run(main())
"""

