import httpx
from core.config import settings
from llm.schemas import JevDepartmentDecision
class JevService:
    def decide(self,state:dict,questions:dict)->JevDepartmentDecision:
        response=httpx.post(settings.jev_base_url,headers={"Authorization":f"Bearer {settings.openrouter_api_key}","Content-Type":"application/json"},json={"model":settings.jev_model,"state":state,"questions":questions},timeout=30.0)
        response.raise_for_status()
        data=response.json()
        answers=data.get("answers")
        if not isinstance(answers,dict):
            raise ValueError("JEV response is missing a valid 'answers' object")
        department=answers.get("department")
        if not isinstance(department,dict):
             raise ValueError("JEV response is missing a valid 'department' decision")
        return JevDepartmentDecision.model_validate(department)