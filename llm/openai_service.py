from langchain_openai import ChatOpenAI
from core.config import settings

class OpenAIService:
    def __init__(self):
        self.llm=ChatOpenAI(
            model="gpt-5.4",
            api_key=settings.openai_api_key,
            temperature=0
        )