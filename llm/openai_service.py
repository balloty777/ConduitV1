from langchain_openai import ChatOpenAI
from core.config import settings

class OpenAIService:
    def __init__(self):
        self.llm=ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0
        )