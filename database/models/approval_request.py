import uuid
from datetime import datetime
from sqlalchemy import ForeignKey,UUID,Text,String,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from zoneinfo import ZoneInfo
from database.database import Base
IST = ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    return datetime.now(IST)


class ApprovalRequest(Base):
    __tablename__="approval_requests"

    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    subject_type:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    subject_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )
    execution_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id"),
        nullable=False
    )
    status:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    reason:Mapped[str|None]=mapped_column(
        Text,
        nullable=True
    )
    decided_by:Mapped[uuid.UUID|None]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_ist
    )
    decided_at:Mapped[datetime|None]=mapped_column(
        DateTime(timezone=True),
        nullable=True
    )