from orchestration.state import State
from llm.openai_service import OpenAIService

def marketing_worker_node(state:State)->State:
    llm=OpenAIService().llm
    response=llm.invoke(state["request"])
    return {
        **state,
        "current_node":"marketing_worker",
        "status":"running",
        "output":response.content
    }