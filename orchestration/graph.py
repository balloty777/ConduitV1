from sqlalchemy.orm import Session
from langgraph.graph import StateGraph,START,END
from orchestration.state import State
from orchestration.nodes.entry import entry_node
from orchestration.nodes.router import router_node
from orchestration.nodes.marketing_worker import marketing_worker_node
from orchestration.node_wrapper import run_node
from orchestration.checkpointer import get_checkpointer
from contextlib import contextmanager
from orchestration.nodes.approval_wait import approval_wait_node

@contextmanager
def build_graph(db:Session):
    graph=StateGraph(State)

    graph.add_node("entry",lambda state: run_node("entry", entry_node,state,db))
    graph.add_node("router",lambda state: run_node("router",router_node,state,db))
    graph.add_node("marketing_worker",lambda state: run_node("marketing_worker",marketing_worker_node,state,db))
    graph.add_node("approval_wait",lambda state:run_node("approval_wait",approval_wait_node,state,db))

    graph.add_edge(START,"entry")
    def route_after_entry(state:State)->str:
        if state["status"]=="failed":
            return "failed"
        return "router"
    graph.add_conditional_edges("entry",route_after_entry,{"router":"router","failed":END})

    def route_department(state:State)->str:
        if state["status"]=="failed":
            return "failed"
        return state["workflow"]
    graph.add_conditional_edges("router",route_department,{"marketing":"marketing_worker","failed":END})
    graph.add_edge("marketing_worker","approval_wait")
    def route_after_approval(state:State)->str:
        if state.get("rejection_reason"):
            return "rejected"
        return "approved"
    graph.add_conditional_edges("approval_wait",route_after_approval,{"rejected":"marketing_worker","approved":END})


    with get_checkpointer() as checkpointer:
        yield graph.compile(checkpointer=checkpointer)