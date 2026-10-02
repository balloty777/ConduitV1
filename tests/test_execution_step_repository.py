from unittest.mock import Mock
from uuid import uuid4
from database.models.execution_steps import ExecutionStep
from database.repositories.execution_step_repository import ExecutionStepRepository

def test_get_by_execution_id_returns_all_steps():
    db = Mock()
    repository = ExecutionStepRepository(db)
    execution_id = uuid4()
    steps = [Mock(), Mock()]
    query = Mock()
    filtered_query = Mock()
    db.query.return_value = query
    query.filter.return_value = filtered_query
    filtered_query.all.return_value = steps
    result = repository.get_by_execution_id(execution_id)
    assert result == steps
    db.query.assert_called_once_with(ExecutionStep)
    query.filter.assert_called_once()
    filtered_query.all.assert_called_once()

def test_delete_step_deletes_and_flushes():
    db = Mock()
    repository = ExecutionStepRepository(db)
    step_id = uuid4()
    step = Mock(spec=ExecutionStep)
    step.id = step_id
    db.get.return_value = step
    result = repository.delete(step_id)
    assert result is None
    db.get.assert_called_once_with(ExecutionStep, step_id)
    db.delete.assert_called_once_with(step)
    db.flush.assert_called_once()

def test_delete_missing_step_does_nothing():
    db = Mock()
    repository = ExecutionStepRepository(db)
    step_id = uuid4()
    db.get.return_value = None
    result = repository.delete(step_id)
    assert result is None
    db.get.assert_called_once_with(ExecutionStep, step_id)
    db.delete.assert_not_called()
    db.flush.assert_not_called()