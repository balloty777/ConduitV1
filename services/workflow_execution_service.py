from uuid import UUID
from sqlalchemy.orm import Session
from database.models.workflow_execution import WorkflowExecution
from database.models.execution_steps import ExecutionStep
from database.repositories.workflow_execution_repository import WorkflowExecutionRepository
from database.repositories.execution_step_repository import ExecutionStepRepository
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")

class WorkflowExecutionService:
    def __init__(self,db:Session):
        self.db=db
        self.workflow_execution_repository=WorkflowExecutionRepository(db)
        self.execution_step_repository=ExecutionStepRepository(db)
    def create_execution(self,user_id:UUID,request:str)->WorkflowExecution:
        execution=WorkflowExecution(user_id=user_id,request=request,status="running")
        try:
            self.workflow_execution_repository.create(execution)
            self.db.commit()
            self.db.refresh(execution)
            return execution
        except Exception:
            self.db.rollback()
            raise
    def create_step(self,execution_id:UUID,node:str,input_data:dict,parent_step_id:UUID|None=None)->ExecutionStep:
        step=ExecutionStep(execution_id=execution_id,parent_step_id=parent_step_id,node=node,input_data=input_data,status="running")
        try:
            self.execution_step_repository.create(step)
            self.db.commit()
            self.db.refresh(step)
            return step
        except Exception:
            self.db.rollback()
            raise

