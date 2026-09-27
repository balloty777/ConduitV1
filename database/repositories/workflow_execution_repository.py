from uuid import UUID
from sqlalchemy.orm import Session
from database.models.workflow_execution import WorkflowExecution

class WorkflowExecutionRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,workflowexecution:WorkflowExecution)->WorkflowExecution:
        self.db.add(workflowexecution)
        self.db.flush()
        return workflowexecution
    def get_by_id(self,execution_id:UUID)->WorkflowExecution|None:
        return self.db.get(WorkflowExecution,execution_id)
    def update(self,workflowexecution:WorkflowExecution)->WorkflowExecution:
        self.db.flush()
        return workflowexecution
    def delete(self,execution_id:UUID)->None:
        workflowexecution=self.db.get(WorkflowExecution,execution_id)
        if workflowexecution is None:
            return None
        self.db.delete(workflowexecution)
        self.db.flush()
        

