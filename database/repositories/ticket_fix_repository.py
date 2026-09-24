from uuid import UUID
from sqlalchemy.orm import Session
from database.models.tech_fix import TechFix

class TechFixRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,tech_fix:TechFix)->TechFix:
        self.db.add(tech_fix)
        self.db.flush()
        return tech_fix
    def get_by_id(self,fix_id)->TechFix|None:
        return self.db.get(TechFix,fix_id)
    def update(self,tech_fix)->TechFix:
        self.db.flush()
        return tech_fix
    def delete(self,fix_id)->None:
        tech_fix=self.db.get(TechFix,fix_id)
        if tech_fix is None:
            return None
        else:
            self.db.delete(tech_fix)
            self.db.flush