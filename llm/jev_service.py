import httpx
from core.config import settings
from mcp_servers.servers.jev.schemas import JevDepartmentDecision
class JevService:
    BASE_URL="https://openrouter.ai/api/alpha/decisions"
    MODEL="typesafe/jev-1.13"
    def decide(self,state:dict,questions:dict)->JevDepartmentDecision:
        response=httpx.post(self.BASE_URL,headers={"Authorization":f"Bearer {settings.openrouter_api_key}","Content-Type":"application/json"},json={"model":self.MODEL,"state":state,"questions":questions},timeout=30.0)
        response.raise_for_status()
        data=response.json()
        decision=JevDepartmentDecision.model_validate(data["answers"]["department"])
        return decision