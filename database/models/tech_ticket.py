import uuid
from sqlalchemy import UUID,DateTime,ForeignKey,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from zoneinfo import ZoneInfo
from database.database import Base
IST = ZoneInfo("Asia/Kolkata")

class TechTicket(Base):
    __tablename__="tech_tickets"

    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    execution_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id"),
        nullable=False,
        index=True
    )
    title:Mapped[str]=mapped_column(
        String(200),
        nullable=False
    )
    category:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    description:Mapped[str]=mapped_column(
        Text,
        nullable=False
    )
    priority:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    status:Mapped[str]=mapped_column(
        String(50),
        nullable=False,
        default="Open"
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