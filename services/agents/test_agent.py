from services.agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    async def get_response(self) -> str:
        return f"Chat history length: {len(self.chat_history)}, newest message: {self.chat_history[-1] if self.chat_history else None}"
