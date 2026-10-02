from unittest.mock import Mock, patch
from uuid import UUID, uuid4
import pytest
from orchestration.nodes.marketing_worker import marketing_worker_node
from orchestration.state import State


def make_state(**overrides) -> State:
    state: State = {
        "request": "Create a LinkedIn post for our new product",
        "user_id": uuid4(),
        "execution_id": uuid4(),
        "current_step_id": None,
        "workflow": "marketing",
        "confidence": 1.0,
        "status": "running",
        "current_node": "marketing_worker",
        "subject_type": None,
        "subject_id": None,
        "approval_request_id": None,
        "rejection_reason": None,
        "output": None,
        "error": None,
    }
    state.update(overrides)
    return state

def make_draft(content="Our new product is here."):
    draft = Mock()
    draft.content = content
    draft.platform = "LinkedIn"
    draft.tone = "professional"
    draft.audience = "B2B founders"
    draft.call_to_action = "Learn more"
    return draft

def make_mcp_result(content_id, execution_id, content="Our new product is here."):
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


def test_marketing_worker_creates_draft_and_approval():
    execution_id = uuid4()
    content_id = uuid4()
    approval_id = uuid4()
    state = make_state(execution_id=execution_id)
    draft = make_draft()
    approval = Mock()
    approval.id = approval_id
    mcp_result = make_mcp_result(content_id=content_id,execution_id=execution_id)
    with patch("orchestration.nodes.marketing_worker.OpenAIService") as mock_openai, patch("orchestration.nodes.marketing_worker.call_mcp_tool",return_value=mcp_result,) as mock_mcp, patch("orchestration.nodes.marketing_worker.ApprovalService") as mock_approval:
        mock_openai.return_value.llm.with_structured_output.return_value.invoke.return_value = draft
        mock_approval.return_value.create_pending.return_value = approval
        result = marketing_worker_node(state, Mock())
    mock_openai.assert_called_once()
    mock_mcp.assert_called_once_with(
        "draft_content",
        {
            "execution_id": str(execution_id),
            "brief": draft.content,
            "platform": draft.platform,
            "tone": draft.tone,
            "audience": draft.audience,
            "call_to_action": draft.call_to_action,
        },
    )
    mock_approval.return_value.create_pending.assert_called_once_with(subject_type="marketing_content",subject_id=content_id,execution_id=execution_id)
    assert result["current_node"] == "marketing_worker"
    assert result["status"] == "running"
    assert result["subject_type"] == "marketing_content"
    assert result["subject_id"] == content_id
    assert result["approval_request_id"] == approval_id
    assert result["output"]["content_id"] == str(content_id)


def test_marketing_worker_includes_rejection_feedback_in_prompt():
    execution_id = uuid4()
    content_id = uuid4()
    approval_id = uuid4()
    rejection_reason = "Make the post shorter and use a stronger CTA."
    state = make_state(execution_id=execution_id,rejection_reason=rejection_reason)
    draft = make_draft(content="New product. Bigger impact. Discover more today.")
    approval = Mock()
    approval.id = approval_id
    mcp_result = make_mcp_result(content_id=content_id,execution_id=execution_id,content=draft.content)
    with patch("orchestration.nodes.marketing_worker.OpenAIService") as mock_openai, patch("orchestration.nodes.marketing_worker.call_mcp_tool",return_value=mcp_result,), patch("orchestration.nodes.marketing_worker.ApprovalService") as mock_approval:
        invoke = (mock_openai.return_value.llm.with_structured_output.return_value.invoke)
        invoke.return_value = draft
        mock_approval.return_value.create_pending.return_value = approval
        result = marketing_worker_node(state, Mock())
    prompt = invoke.call_args.args[0]
    assert rejection_reason in prompt
    assert "The previous draft was rejected." in prompt
    assert "Revise the content based on this feedback." in prompt
    assert result["subject_id"] == content_id
    assert result["approval_request_id"] == approval_id


def test_marketing_worker_does_not_include_rejection_section_without_feedback():
    execution_id = uuid4()
    content_id = uuid4()
    approval_id = uuid4()
    state = make_state(execution_id=execution_id,rejection_reason=None)
    draft = make_draft()
    approval = Mock()
    approval.id = approval_id
    mcp_result = make_mcp_result(content_id=content_id,execution_id=execution_id)
    with patch("orchestration.nodes.marketing_worker.OpenAIService") as mock_openai, patch("orchestration.nodes.marketing_worker.call_mcp_tool",return_value=mcp_result,), patch("orchestration.nodes.marketing_worker.ApprovalService") as mock_approval:
        invoke = (mock_openai.return_value.llm.with_structured_output.return_value.invoke)
        invoke.return_value = draft
        mock_approval.return_value.create_pending.return_value = approval
        marketing_worker_node(state, Mock())
    prompt = invoke.call_args.args[0]
    assert "The previous draft was rejected." not in prompt
    assert "Rejection feedback:" not in prompt


def test_marketing_worker_propagates_llm_error():
    state = make_state()
    with patch("orchestration.nodes.marketing_worker.OpenAIService") as mock_openai:
        invoke = (mock_openai.return_value.llm.with_structured_output.return_value.invoke)
        invoke.side_effect = RuntimeError("LLM unavailable")
        with pytest.raises(RuntimeError, match="LLM unavailable"):
            marketing_worker_node(state, Mock())


def test_marketing_worker_propagates_mcp_error():
    state = make_state()
    draft = make_draft()
    with patch("orchestration.nodes.marketing_worker.OpenAIService") as mock_openai, patch("orchestration.nodes.marketing_worker.call_mcp_tool") as mock_mcp:
        mock_openai.return_value.llm.with_structured_output.return_value.invoke.return_value = draft
        mock_mcp.side_effect = RuntimeError("MCP unavailable")
        with pytest.raises(RuntimeError, match="MCP unavailable"):
            marketing_worker_node(state, Mock())


def test_marketing_worker_converts_subject_id_to_uuid():
    execution_id = uuid4()
    content_id = uuid4()
    approval_id = uuid4()
    state = make_state(execution_id=execution_id)
    draft = make_draft()
    approval = Mock()
    approval.id = approval_id
    mcp_result = make_mcp_result(content_id=content_id,execution_id=execution_id)
    with patch("orchestration.nodes.marketing_worker.OpenAIService") as mock_openai, patch("orchestration.nodes.marketing_worker.call_mcp_tool",return_value=mcp_result), patch("orchestration.nodes.marketing_worker.ApprovalService") as mock_approval:
        mock_openai.return_value.llm.with_structured_output.return_value.invoke.return_value = draft
        mock_approval.return_value.create_pending.return_value = approval
        result = marketing_worker_node(state, Mock())
    assert isinstance(result["subject_id"], UUID)
    assert result["subject_id"] == content_id