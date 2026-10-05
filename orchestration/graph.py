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
from orchestration.nodes.sales_worker import sales_worker_node,sales_follow_up_worker_node
from orchestration.nodes.tech_worker import tech_worker_node,tech_fix_worker_node

@contextmanager
def build_graph(db:Session):
    graph=StateGraph(State)

    graph.add_node("entry",lambda state: run_node("entry", entry_node,state,db))
    graph.add_node("router",lambda state: run_node("router",router_node,state,db))
    graph.add_node("marketing_worker",lambda state: run_node("marketing_worker",marketing_worker_node,state,db))
    graph.add_node("approval_wait",lambda state:run_node("approval_wait",approval_wait_node,state,db))
    graph.add_node("sales_worker",lambda state: run_node("sales_worker",sales_worker_node,state,db))
    graph.add_node("sales_follow_up_worker",lambda state: run_node("sales_follow_up_worker",sales_follow_up_worker_node,state,db))
    graph.add_node("tech_worker",lambda state: run_node("tech_worker",tech_worker_node,state,db))
    graph.add_node("tech_fix_worker",lambda state: run_node("tech_fix_worker",tech_fix_worker_node,state,db))

    graph.add_edge(START,"entry")
    def route_after_entry(state:State)->str:
        if state["status"]=="failed":
            return "failed"
        return "router"
    graph.add_conditional_edges("entry",route_after_entry,{"router":"router","failed":END})

    def route_action(state:State)->str:
        if state["status"]=="failed":
            return "failed"
        return state["action"]
    graph.add_conditional_edges("router",route_action,{"create_content":"marketing_worker","create_lead":"sales_worker","follow_up_lead":"sales_follow_up_worker","create_ticket":"tech_worker","create_ticket_fix":"tech_fix_worker","failed":END})
    graph.add_edge("marketing_worker","approval_wait")
    graph.add_edge("sales_worker","approval_wait")
    graph.add_edge("sales_follow_up_worker","approval_wait")
    graph.add_edge("tech_worker","approval_wait")
    graph.add_edge("tech_fix_worker","approval_wait")
    
    def route_after_approval(state:State)->str:
        if state.get("rejection_reason"):
            return state["action"]
        return "approved"
    graph.add_conditional_edges("approval_wait",route_after_approval,{"create_content":"marketing_worker","create_lead":"sales_worker","follow_up_lead":"sales_follow_up_worker","create_ticket":"tech_worker","create_ticket_fix":"tech_fix_worker","approved":END})


    with get_checkpointer() as checkpointer:
        yield graph.compile(checkpointer=checkpointer)