import uuid
from sqlalchemy import UUID,ForeignKey,String,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from database.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")

class SalesLead(Base):
    __tablename__="sales_leads"

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
    name:Mapped[str]=mapped_column(
        String(200),
        nullable=False
    )
    email:Mapped[str]=mapped_column(
        String(300),
        nullable=False
    )
    phone:Mapped[str|None]=mapped_column(
        String(30),
        nullable=True
    )
    status:Mapped[str]=mapped_column(
        String(30),
        default="New",
        nullable=False
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
