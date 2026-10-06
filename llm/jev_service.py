import httpx
from core.config import settings
from llm.schemas import JevDecision
class JevService:
    def decide(self,state:dict,questions:dict)->JevDecision:
        response=httpx.post(settings.jev_base_url,headers={"Authorization":f"Bearer {settings.openrouter_api_key}","Content-Type":"application/json"},json={"model":settings.jev_model,"state":state,"questions":questions},timeout=30.0)
        response.raise_for_status()
        data=response.json()
        answers=data.get("answers")
        if not isinstance(answers,dict):
            raise ValueError("JEV response is missing a valid 'answers' object")
        decision_key=next(iter(questions.keys()))
        decision=answers.get(decision_key)
        if not isinstance(decision,dict):
             raise ValueError("JEV response is missing a valid 'department' decision")
        return JevDecision.model_validate(decision)