
from models.models import LLMResponse


async def get_llm_response(prompt: dict) -> LLMResponse:
    return LLMResponse(response='Sample LLM Response')