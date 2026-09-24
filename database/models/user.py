import uuid
from sqlalchemy import UUID,String, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped,mapped_column
from database.database import Base
class User(Base):
    __tablename__="users"
    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )   

    email:Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    role:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    team:Mapped[str]=mapped_column(
        String(20),
        nullable=False
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