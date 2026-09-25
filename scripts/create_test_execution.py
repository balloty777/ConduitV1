from database.database import get_session
from database.models.user import User
from database.models.workflow_execution import WorkflowExecution


with get_session() as db:

    user = User(
        email="test@conduit.local",
        role="admin",
        team="marketing",
    )

    db.add(user)
    db.flush()

    execution = WorkflowExecution(
        user_id=user.id,
        request="Create a test marketing content draft",
        workflow="marketing",
        status="pending",
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    print(f"User ID: {user.id}")
    print(f"Execution ID: {execution.id}")