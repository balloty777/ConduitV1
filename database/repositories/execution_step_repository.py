from uuid import UUID
from sqlalchemy.orm import Session
from database.models.execution_steps import ExecutionStep

class ExecutionStepRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,execution_step:ExecutionStep)->ExecutionStep:
        self.db.add(execution_step)
        self.db.flush()
        return execution_step
    def get_by_id(self,step_id:UUID)->ExecutionStep|None:
        return self.db.get(ExecutionStep,step_id)
    def get_by_execution_id(self,execution_id:UUID)->list[ExecutionStep]:
        return (self.db.query(ExecutionStep).filter(ExecutionStep.execution_id==execution_id).all())
    def update(self,execution_step:ExecutionStep)->ExecutionStep:
        self.db.flush()
        return execution_step
    def delete(self,step_id:UUID)->None:
        step=self.db.get(ExecutionStep,step_id)
        if step is None:
            return None
        self.db.delete(step)
        self.db.flush()