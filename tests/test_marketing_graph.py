from unittest.mock import Mock, patch
from uuid import uuid4
from langgraph.types import Command
from database.database import get_session
from orchestration.graph import build_graph
from services.workflow_execution_service import WorkflowExecutionService
from database.models.user import User

def make_state(user_id, execution_id):
    return {
        "request": "Create a LinkedIn post for our new product",
        "user_id": user_id,
        "execution_id": execution_id,
        "current_step_id": None,
        "workflow": None,
        "confidence": None,
        "status": "pending",
        "current_node": None,
        "subject_type": None,
        "subject_id": None,
        "approval_request_id": None,
        "rejection_reason": None,
        "output": None,
        "error": None,
    }


def make_draft(content):
    draft = Mock()
    draft.content = content
    draft.platform = "LinkedIn"
    draft.tone = "professional"
    draft.audience = "B2B founders"
    draft.call_to_action = "Learn more"
    return draft


def make_mcp_result(content_id, execution_id, content):
    return [
        {
            "text": (
                "{"
                f'"content_id": "{content_id}", '
                f'"execution_id": "{execution_id}", '
                '"platform": "LinkedIn", '
                f'"content": "{content}", '
                '"tone": "professional", '
                '"audience": "B2B founders", '
                '"call_to_action": "Learn more", '
                '"status": "draft"'
                "}"
            )
        }
    ]


@patch("orchestration.nodes.router.JevService")
@patch("orchestration.nodes.marketing_worker.call_mcp_tool")
@patch("orchestration.nodes.marketing_worker.OpenAIService")
def test_marketing_graph_reject_then_approve(mock_openai,mock_mcp,mock_jev):
    user_id = uuid4()
    first_content_id = uuid4()
    second_content_id = uuid4()
    first_draft = make_draft("Our new product is here. Discover what's possible.")
    second_draft = make_draft("Meet our new product. Built for teams ready to move faster.")
    mock_jev.return_value.decide.return_value = Mock(choice="marketing",confidence=1.0)
    invoke = (mock_openai.return_value.llm.with_structured_output.return_value.invoke)
    invoke.side_effect = [first_draft,second_draft]
    mock_mcp.side_effect = [make_mcp_result(first_content_id,Mock(),first_draft.content,),make_mcp_result(second_content_id,Mock(),second_draft.content)]

    with get_session() as db:
        user=User(id=user_id,email=f"graph-test-{uuid4()}@conduit.local",role="admin",team="Management")
        db.add(user)
        db.flush()
        execution_service = WorkflowExecutionService(db)
        execution = execution_service.create_execution(user_id=user_id,request="Create a LinkedIn post for our new product")
        execution_id = execution.id
        mock_mcp.side_effect = [make_mcp_result(first_content_id,execution_id,first_draft.content),make_mcp_result(second_content_id,execution_id,second_draft.content)]
        state = make_state(user_id=user_id,execution_id=execution_id)
        with build_graph(db) as graph:
            config = {"configurable": {"thread_id": str(execution_id)}}
            first_result = graph.invoke(state,config=config)
            assert "__interrupt__" in first_result
            interrupt_payload = first_result["__interrupt__"][0].value
            assert interrupt_payload["type"] == "approval_required"
            assert interrupt_payload["subject_type"] == "marketing_content"
            assert interrupt_payload["subject_id"] == first_content_id
            rejected_result = graph.invoke(Command(resume={"decision": "rejected","reason": "Make the post shorter and strengthen the CTA."}),config=config)
            assert "__interrupt__" in rejected_result
            second_interrupt = rejected_result["__interrupt__"][0].value
            assert second_interrupt["type"] == "approval_required"
            assert second_interrupt["subject_type"] == "marketing_content"
            assert second_interrupt["subject_id"] == second_content_id
            final_result = graph.invoke(Command(resume={"decision": "approved",}),config=config,)
    assert "__interrupt__" not in final_result
    assert final_result["rejection_reason"] is None
    assert final_result["subject_id"] == second_content_id
    assert final_result["output"]["content_id"] == str(second_content_id)
    assert invoke.call_count == 2
    first_prompt = invoke.call_args_list[0].args[0]
    second_prompt = invoke.call_args_list[1].args[0]
    assert "Create a LinkedIn post for our new product" in first_prompt
    assert "Make the post shorter and strengthen the CTA." in second_prompt
    assert mock_mcp.call_count == 2