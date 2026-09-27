import uuid
from sqlalchemy import UUID,DateTime,ForeignKey,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from zoneinfo import ZoneInfo
from database.database import Base
IST = ZoneInfo("Asia/Kolkata")

class SalesFollowUp(Base):
    __tablename__ = "sales_follow_ups"

    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    lead_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_leads.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    execution_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id"),
        nullable=False,
        index=True
    )
    message:Mapped[str]=mapped_column(
        Text,
        nullable=False
    )
    channel:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    status:Mapped[str]=mapped_column(
        String(50),
        nullable=False,
        default="No Follow ups yet"
    )
    scheduled_at:Mapped[datetime|None]=mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda:datetime.now(IST)
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(IST),
        onupdate=lambda: datetime.now(IST)
    )