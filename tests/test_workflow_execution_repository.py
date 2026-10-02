from unittest.mock import Mock
from uuid import uuid4
from database.models.workflow_execution import WorkflowExecution
from database.repositories.workflow_execution_repository import WorkflowExecutionRepository

def test_delete_execution_deletes_and_flushes():
    db = Mock()
    repository = WorkflowExecutionRepository(db)
    execution_id = uuid4()
    execution = Mock(spec=WorkflowExecution)
    execution.id = execution_id
    db.get.return_value = execution
    result = repository.delete(execution_id)
    assert result is None
    db.get.assert_called_once_with(WorkflowExecution, execution_id)
    db.delete.assert_called_once_with(execution)
    db.flush.assert_called_once()

def test_delete_missing_execution_does_nothing():
    db = Mock()
    repository = WorkflowExecutionRepository(db)
    execution_id = uuid4()
    db.get.return_value = None
    result = repository.delete(execution_id)
    assert result is None
    db.get.assert_called_once_with(WorkflowExecution, execution_id)
    db.delete.assert_not_called()
    db.flush.assert_not_called()