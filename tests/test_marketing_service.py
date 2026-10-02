from datetime import datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from services.marketing_service import MarketingService
from exceptions.exceptions import ResourceNotFoundException,InvalidStateTransitionException



def make_service():
    db = Mock()
    service = MarketingService(db)
    service.repository = Mock()
    return service, db


def test_draft_content_creates_draft():
    service, db = make_service()
    execution_id = uuid4()
    created_content = Mock()
    service.repository.create.return_value = created_content
    result = service.draft_content(execution_id=execution_id,brief="Create a LinkedIn post about our new product.",platform="LinkedIn",tone="professional",audience="B2B marketers",call_to_action="Learn more")
    created_request = service.repository.create.call_args.kwargs["marketing_content"]
    assert result is created_content
    assert created_request.execution_id == execution_id
    assert created_request.content == "Create a LinkedIn post about our new product."
    assert created_request.platform == "LinkedIn"
    assert created_request.tone == "professional"
    assert created_request.audience == "B2B marketers"
    assert created_request.call_to_action == "Learn more"
    assert created_request.status == "draft"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_content)


def test_get_content_returns_existing_content():
    service, _ = make_service()
    content_id = uuid4()
    content = Mock()
    service.repository.get_by_id.return_value = content
    result = service.get_content(content_id)
    assert result is content
    service.repository.get_by_id.assert_called_once_with(content_id)


def test_get_content_raises_when_missing():
    service, _ = make_service()
    service.repository.get_by_id.return_value = None
    with pytest.raises(ResourceNotFoundException):
        service.get_content(uuid4())


def test_update_draft_content():
    service, db = make_service()
    content_id = uuid4()
    content = Mock()
    content.id = content_id
    content.status = "draft"
    service.repository.get_by_id.return_value = content
    service.repository.update.return_value = content
    result = service.update_content(content_id=content_id,brief="Updated LinkedIn content",platform="LinkedIn",tone="friendly",audience="Developers",call_to_action="Try it now")
    assert result is content
    assert content.content == "Updated LinkedIn content"
    assert content.platform == "LinkedIn"
    assert content.tone == "friendly"
    assert content.audience == "Developers"
    assert content.call_to_action == "Try it now"
    service.repository.update.assert_called_once_with(content)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(content)

def test_cannot_update_non_draft_content():
    service, _ = make_service()
    content = Mock()
    content.status = "scheduled"
    service.repository.get_by_id.return_value = content
    with pytest.raises(InvalidStateTransitionException):
        service.update_content(content_id=uuid4(),brief="Updated content",platform="LinkedIn",tone="professional",audience="Developers")
    service.repository.update.assert_not_called()


def test_schedule_draft_content():
    service, db = make_service()
    content_id = uuid4()
    content = Mock()
    content.id = content_id
    content.status = "draft"
    service.repository.get_by_id.return_value = content
    service.repository.update.return_value = content
    scheduled_at = datetime.now(service.__class__.__dict__["schedule_content"].__globals__["IST"]) + timedelta(hours=2)
    result = service.schedule_content(
    content_id=content_id,scheduled_at=scheduled_at)
    assert result is content
    assert content.status == "scheduled"
    assert content.scheduled_at == scheduled_at
    service.repository.update.assert_called_once_with(content)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(content)


def test_cannot_schedule_content_in_the_past():
    service, _ = make_service()
    content = Mock()
    content.status = "draft"
    service.repository.get_by_id.return_value = content
    past_time = datetime.now(service.__class__.__dict__["schedule_content"].__globals__["IST"]) - timedelta(hours=1)
    with pytest.raises(InvalidStateTransitionException):
        service.schedule_content(content_id=uuid4(),scheduled_at=past_time)
    service.repository.update.assert_not_called()

def test_cannot_schedule_non_draft_content():
    service, _ = make_service()
    content = Mock()
    content.status = "scheduled"
    service.repository.get_by_id.return_value = content
    future_time = datetime.now(service.__class__.__dict__["schedule_content"].__globals__["IST"]) + timedelta(hours=2)
    with pytest.raises(InvalidStateTransitionException):
        service.schedule_content(content_id=uuid4(),scheduled_at=future_time)
    service.repository.update.assert_not_called()

def test_delete_content():
    service, db = make_service()
    content_id = uuid4()
    content = Mock()
    content.id = content_id
    service.repository.get_by_id.return_value = content
    result = service.delete_content(content_id)
    assert result is None
    service.repository.delete.assert_called_once_with(content_id)
    db.commit.assert_called_once()