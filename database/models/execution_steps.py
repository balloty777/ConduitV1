import uuid
from sqlalchemy import UUID,ForeignKey,String,JSON,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database.database import Base
from datetime import datetime

class ExecutionStep(Base):
    __tablename__="execution_steps"
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
    parent_step_id:Mapped[uuid.UUID|None]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("execution_steps.id"),
        nullable=True,
        index=True
    )
    node:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )
    input_data:Mapped[dict]=mapped_column(
        JSON,
        nullable=False
    )
    output_data:Mapped[dict|None]=mapped_column(
        JSON,
        nullable=True
    )
    status:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=datetime.now
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now
    )
    execution: Mapped["WorkflowExecution"] = relationship(
        "WorkflowExecution",
        back_populates="steps",
    )
    parent: Mapped["ExecutionStep | None"] = relationship(
        "ExecutionStep",
        remote_side=[id],
        back_populates="children",
    )

    children: Mapped[list["ExecutionStep"]] = relationship(
        "ExecutionStep",
        back_populates="parent",
    )