import uuid
from sqlalchemy import UUID,ForeignKey,String,Text,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from database.database import Base
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")

class MarketingContent(Base):
    __tablename__="marketing_contents"

    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    execution_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id"),
        nullable=False
    )
    platform:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    content:Mapped[str]=mapped_column(
        Text,
        nullable=False
    )
    tone:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    audience:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    call_to_action:Mapped[str|None]=mapped_column(
        String(150),
        nullable=True
    )
    status:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    scheduled_at:Mapped[datetime|None]=mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(IST)
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(IST),
        onupdate=lambda: datetime.now(IST)
    )