from uuid import UUID
from sqlalchemy.orm import Session
from database.models.workflow_execution import WorkflowExecution
from database.models.execution_steps import ExecutionStep
from database.repositories.workflow_execution_repository import WorkflowExecutionRepository
from database.repositories.execution_step_repository import ExecutionStepRepository
from exceptions.exceptions import ResourceNotFoundException
import json
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
    def complete_step(self,step:ExecutionStep,output_data:dict)->ExecutionStep:
        step.output_data=output_data
        step.status="completed"
        try:
            self.execution_step_repository.update(step)
            self.db.commit()
            self.db.refresh(step)
            return step
        except Exception:
            self.db.rollback()
            raise
    def fail_step(self,step:ExecutionStep,error:str)->ExecutionStep:
        step.output_data={"error":error}
        step.status="failed"
        try:
            self.execution_step_repository.update(step)
            self.db.commit()
            self.db.refresh(step)
            return step
        except Exception:
            self.db.rollback()
            raise
    def fail_execution(self,execution_id:UUID,error:str)->WorkflowExecution:
        execution=self.workflow_execution_repository.get_by_id(execution_id)
        if execution is None:
            raise ResourceNotFoundException(f"Workflow execution not found: {execution_id}")
        execution.status="failed"
        execution.result=error
        try:
            self.workflow_execution_repository.update(execution)
            self.db.commit()
            self.db.refresh(execution)
            return execution
        except Exception:
            self.db.rollback()
            raise
    def complete_execution(self,execution_id:UUID,result:dict|None=None)->WorkflowExecution:
        execution=self.workflow_execution_repository.get_by_id(execution_id)
        if execution is None:
            raise ResourceNotFoundException(f"Workflow execution not found: {execution_id}")
        execution.status="completed"
        if result is None:
            execution.result=json.dumps(result,default=str)
        else:
            execution.result=None
        try:
            self.workflow_execution_repository.update(execution)
            self.db.commit()
            self.db.refresh(execution)
            return execution
        except Exception:
            self.db.rollback()
            raise


