from sqlalchemy.orm import Session
from langgraph.graph import StateGraph,START,END
from orchestration.state import State
from orchestration.nodes.entry import entry_node
from orchestration.nodes.router import router_node
from orchestration.nodes.marketing_worker import marketing_worker_node

def build_graph(db:Session):
    graph=StateGraph(State)
    graph.add_node("entry",lambda state: entry_node(state,db))
    graph.add_node("router",router_node)
    graph.add_node("marketing_worker",marketing_worker_node)

    graph.add_edge(START,"entry")
    graph.add_edge("entry","router")

    def route_department(state:State)->str:
        return state["workflow"]
    
    graph.add_conditional_edges("router",route_department,{"marketing":"marketing_worker"})
    graph.add_edge("marketing_worker",END)

    return graph.compile()