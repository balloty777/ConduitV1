from unittest.mock import Mock
from uuid import uuid4
from services.workflow_execution_service import WorkflowExecutionService
import json

def test_complete_execution_persists_result():
    execution_id=uuid4()
    execution=Mock()
    execution.id=execution_id
    db=Mock()
    service=WorkflowExecutionService(db)
    service.workflow_execution_repository=Mock()
    service.workflow_execution_repository.get_by_id.return_value=execution
    result={"request":"Create a marketing campaign","workflow":"marketing","status":"completed"}
    returned=service.complete_execution(execution_id=execution_id,result=result)
    assert returned is execution
    assert execution.status=="completed"
    assert json.loads(execution.result)==result

def test_complete_execution_with_no_result_sets_none():
    execution_id=uuid4()
    execution=Mock()
    execution.id=execution_id
    db=Mock()
    service=WorkflowExecutionService(db)
    service.workflow_execution_repository=Mock()
    service.workflow_execution_repository.get_by_id.return_value=execution
    returned = service.complete_execution(execution_id=execution_id,result=None)
    assert returned is execution
    assert execution.status=="completed"
    assert execution.result is None