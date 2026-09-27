import uuid

from database.database import SessionLocal
from database.models.user import User
from database.models.workflow_execution import WorkflowExecution

with SessionLocal() as db:
    user = User(
        email="test5@conduit.local",
        role="admin",
        team="Management"
    )

    db.add(user)
    db.flush()

    execution = WorkflowExecution(
        user_id=user.id,
        request="Announce our new AI workflow automation feature",
        workflow="Marketing",
        status="pending"
    )

    db.add(execution)
    db.flush()

    db.commit()
    db.refresh(execution)

    print(f"user_id: {user.id}")
    print(f"execution_id: {execution.id}")