from unittest.mock import Mock, patch
from uuid import uuid4
from mcp_servers.servers.marketing.schemas import DraftContentInput,GetContentInput
from mcp_servers.servers.marketing.server import draft_content,get_content
import pytest
from pydantic import ValidationError
from exceptions.exceptions import ResourceNotFoundException
from mcp_servers.servers.marketing.schemas import DraftContentInput

def test_draft_content_calls_service_and_returns_output():
    execution_id = uuid4()
    content_id = uuid4()
    data = DraftContentInput(execution_id=execution_id,brief="Launch our new product",platform="LinkedIn",tone="professional",audience="B2B founders",call_to_action="Learn more")
    content = Mock()
    content.id = content_id
    content.execution_id = execution_id
    content.platform = "LinkedIn"
    content.content = "Launch our new product"
    content.tone = "professional"
    content.audience = "B2B founders"
    content.call_to_action = "Learn more"
    content.status = "draft"
    mock_db = Mock()
    mock_context = Mock()
    mock_context.__enter__ = Mock(return_value=mock_db)
    mock_context.__exit__ = Mock(return_value=False)
    with patch("mcp_servers.servers.marketing.server.get_session",return_value=mock_context), patch("mcp_servers.servers.marketing.server.MarketingService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.draft_content.return_value = content
        result = draft_content(data)
    mock_service_class.assert_called_once_with(mock_db)
    mock_service.draft_content.assert_called_once_with(execution_id=execution_id,brief="Launch our new product",platform="LinkedIn",tone="professional",audience="B2B founders",call_to_action="Learn more")
    assert result.content_id == content_id
    assert result.execution_id == execution_id
    assert result.platform == "LinkedIn"
    assert result.content == "Launch our new product"
    assert result.tone == "professional"
    assert result.audience == "B2B founders"
    assert result.call_to_action == "Learn more"
    assert result.status == "draft"


def test_get_content_calls_service_and_returns_output():
    content_id = uuid4()
    execution_id = uuid4()
    data = GetContentInput(content_id=content_id)
    content = Mock()
    content.id = content_id
    content.execution_id = execution_id
    content.platform = "LinkedIn"
    content.content = "Our new product is here"
    content.tone = "professional"
    content.audience = "B2B founders"
    content.call_to_action = "Learn more"
    content.status = "draft"
    content.scheduled_at = None
    mock_db = Mock()
    mock_context = Mock()
    mock_context.__enter__ = Mock(return_value=mock_db)
    mock_context.__exit__ = Mock(return_value=False)
    with patch("mcp_servers.servers.marketing.server.get_session",return_value=mock_context), patch("mcp_servers.servers.marketing.server.MarketingService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.get_content.return_value = content
        result = get_content(data)
    mock_service_class.assert_called_once_with(mock_db)
    mock_service.get_content.assert_called_once_with(content_id=content_id)
    assert result.content_id == content_id
    assert result.execution_id == execution_id
    assert result.platform == "LinkedIn"
    assert result.content == "Our new product is here"
    assert result.tone == "professional"
    assert result.audience == "B2B founders"
    assert result.call_to_action == "Learn more"
    assert result.status == "draft"
    assert result.scheduled_at is None

def test_get_content_propagates_not_found():
    content_id = uuid4()
    data = GetContentInput(content_id=content_id)
    mock_db = Mock()
    mock_context = Mock()
    mock_context.__enter__ = Mock(return_value=mock_db)
    mock_context.__exit__ = Mock(return_value=False)
    with patch("mcp_servers.servers.marketing.server.get_session",return_value=mock_context,), patch("mcp_servers.servers.marketing.server.MarketingService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.get_content.side_effect = ResourceNotFoundException(f"Marketing content for {content_id} does not exist")
        with pytest.raises(ResourceNotFoundException):
            get_content(data)

def test_draft_content_propagates_service_error():
    execution_id = uuid4()
    data = DraftContentInput(execution_id=execution_id,brief="Launch our new product",platform="LinkedIn",tone="professional",audience="B2B founders",call_to_action="Learn more")
    mock_db = Mock()
    mock_context = Mock()
    mock_context.__enter__ = Mock(return_value=mock_db)
    mock_context.__exit__ = Mock(return_value=False)
    with patch("mcp_servers.servers.marketing.server.get_session",return_value=mock_context), patch("mcp_servers.servers.marketing.server.MarketingService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.draft_content.side_effect = RuntimeError("database failure")
        with pytest.raises(RuntimeError, match="database failure"):
            draft_content(data)

def test_draft_content_schema_rejects_invalid_execution_id():
    with pytest.raises(ValidationError):
        DraftContentInput(execution_id="not-a-uuid",brief="Launch our new product",platform="LinkedIn",tone="professional",audience="B2B founders",call_to_action="Learn more")