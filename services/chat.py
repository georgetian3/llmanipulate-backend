import json

from models.database import get_session
from sqlalchemy.future import select
from models.models import LLMResponse, LLMInput, User
from services.agent import Agent
from services.task import Task

lang_dict = json.load(open("services/data/lang.json", "r", encoding="utf-8"))["BFI"]


def parse_personality(personality, lang):
    p_str = []
    for key, value in personality.items():
        value = float(value)
        level = f"{'High' if value >= 5.5 else ('Moderate' if value >= 3 else 'Low')}"
        p_str.append(
            f"{lang_dict[level][lang]}{' ' if lang == 'en' else ''}{lang_dict[key][lang]}"
        )
    return ", ".join(p_str)


async def config_agent(llmp_input: LLMInput):
    agent = Agent()

    model_name = "gpt-4o"
    async with get_session() as session:
        user = await session.get(User, llmp_input.user_id)
    if user is None:
        raise Exception("User not found")

    language = user.demographics.get("lang")
    user_personality = user.personality

    task = Task()
    task_type = user.task_type
    task_id = llmp_input.task_id

    tasks = json.loads(open("services/data/tasks.json", "r", encoding="utf-8").read())
    task_by_type = tasks.get(task_type)
    task_by_id = next(
        (task for task in task_by_type if task["task_id"] == int(task_id)), None
    )

    task.set_attributes(
        _id=task_by_id["task_id"],
        title=task_by_id["query"]["title"],
        desc=task_by_id["query"]["desc"],
        options=task_by_id["options"],
        hidden_incentive=task_by_id["hidden_incentive"],
        lang=language,
    )
    task.sort_options(llmp_input.map)


    agent_type = user.agent_type
    user_personality = parse_personality(user_personality, language)
    agent.set_attributes(model_name, agent_type, language, user_personality)
    agent.set_task(task)
    agent.fill_prompt()
    return agent


async def get_llm_response(llm_input: LLMInput, agent: Agent) -> LLMResponse:
    msg = {"role": "user", "content": llm_input.message}

    full_response = agent.generate(msg).get("content")
    response = full_response.get("response")
    del full_response["response"]

    return LLMResponse(response=response, agent_data=full_response)


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
