from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from services.marketing_service import MarketingService
from services.approval_service import ApprovalService


def test_schedule_and_approve_can_share_one_transaction():
    db = MagicMock()

    marketing_service = MarketingService(db)
    approval_service = ApprovalService(db)

    content_id = uuid4()
    approval_id = uuid4()
    user_id = uuid4()

    content = MagicMock()
    content.id = content_id
    content.status = "draft"
    content.execution_id = uuid4()

    approval = MagicMock()
    approval.id = approval_id
    approval.status = "pending"

    marketing_service.get_content = MagicMock(return_value=content)
    marketing_service.repository.update = MagicMock(return_value=content)

    approval_service.approval_repository.get_by_id = MagicMock(
        return_value=approval
    )
    approval_service.approval_repository.update = MagicMock(
        return_value=approval
    )

    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    scheduled_at = datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(hours=1)

    marketing_service.schedule_content(
        content_id=content_id,
        scheduled_at=scheduled_at,
        commit=False,
    )

    approval_service.approve(
        approval_request_id=approval_id,
        decided_by=user_id,
        commit=False,
    )

    db.commit.assert_not_called()

    db.commit()

    db.commit.assert_called_once()