from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from api.schemas.approval import ApprovalResponse,RejectApprovalRequest,ApproveApprovalRequest
from services.workflow_execution_service import WorkflowExecutionService
from langgraph.types import Command
from orchestration.graph import build_graph
from services.approval_service import ApprovalService

router=APIRouter(prefix="/approvals",tags=["Approvals"])    

@router.post("/{approval_request_id}/approve",response_model=ApprovalResponse)
def approve_approval(approval_request_id:UUID,data:ApproveApprovalRequest,db:Session=Depends(get_db)):
    approval_service=ApprovalService(db)
    workflow_service=WorkflowExecutionService(db)
    approval_request=approval_service.approve(approval_request_id=approval_request_id,decided_by=data.user_id,commit=True)
    with build_graph(db) as graph:
        final_state=graph.invoke(
            Command(resume={"decision":"approved"}),
            config={"configurable": {"thread_id": str(approval_request.execution_id)}}
        )
    if approval_request.subject_type not in {"marketing_content","sales_follow_up"}:
        workflow_service.complete_execution(execution_id=approval_request.execution_id,result=final_state)
    return ApprovalResponse(approval_request_id=approval_request.id,execution_id=approval_request.execution_id,subject_type=approval_request.subject_type,subject_id=approval_request.subject_id,status=approval_request.status,reason=approval_request.reason,decided_by=approval_request.decided_by)

@router.post("/{approval_request_id}/reject",response_model=ApprovalResponse)
def reject_approval(approval_request_id:UUID,data:RejectApprovalRequest,db:Session=Depends(get_db)):
    approval_service=ApprovalService(db)
    approval_request=approval_service.reject(approval_request_id=approval_request_id,decided_by=data.user_id,reason=data.reason)
    with build_graph(db) as graph:
        graph.invoke(
            Command(resume={"decision":"rejected","reason":data.reason}),
            config={"configurable": {"thread_id": str(approval_request.execution_id)}}
        )

    return ApprovalResponse(approval_request_id=approval_request.id,execution_id=approval_request.execution_id,subject_type=approval_request.subject_type,subject_id=approval_request.subject_id,status=approval_request.status,reason=approval_request.reason,decided_by=approval_request.decided_by)