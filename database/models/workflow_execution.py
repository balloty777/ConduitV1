import uuid
from sqlalchemy import UUID,ForeignKey,Text,String,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database.database import Base
from datetime import datetime

class WorkflowExecution(Base):
    __tablename__="workflow_executions"
    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    request:Mapped[str]=mapped_column(
        Text,
        nullable=False
    )
    workflow:Mapped[str|None]=mapped_column(
        String(20),
        nullable=True
    )
    status:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    result:Mapped[str|None]=mapped_column(
        Text,
        nullable=True
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now
    )
    updated_by:Mapped[uuid.UUID|None]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    steps: Mapped[list["ExecutionStep"]] = relationship(
        "ExecutionStep",
        back_populates="execution",
        cascade="all, delete-orphan"
    )