from uuid import UUID
from pydantic import BaseModel


class CreateTicketInput(BaseModel):
    execution_id: UUID
    title: str
    category: str
    description: str
    proposed_fix:str
    priority: str


class CreateTicketOutput(BaseModel):
    ticket_id: UUID
    execution_id: UUID
    title: str
    category: str
    description: str
    proposed_fix:str
    priority: str
    status: str


class DeleteTicketInput(BaseModel):
    ticket_id: UUID


class DeleteTicketOutput(BaseModel):
    ticket_id: UUID
    deleted: bool


class TicketFixInput(BaseModel):
    ticket_id: UUID
    execution_id: UUID
    proposed_fix: str


class TicketFixOutput(BaseModel):
    fix_id: UUID
    ticket_id: UUID
    execution_id: UUID
    proposed_fix: str
    status: str


class UpdateTicketInput(BaseModel):
    ticket_id: UUID
    execution_id: UUID
    title: str
    category: str
    description: str
    proposed_fix:str
    priority: str


class UpdateTicketOutput(BaseModel):
    ticket_id: UUID
    execution_id: UUID
    title: str
    category: str
    description: str
    proposed_fix:str
    priority: str
    status:str

class UpdateTicketFixInput(BaseModel):
    fix_id: UUID
    execution_id: UUID
    proposed_fix: str


class UpdateTicketFixOutput(BaseModel):
    fix_id: UUID
    ticket_id: UUID
    execution_id: UUID
    proposed_fix: str
    status: str

class GetTicketInput(BaseModel):
    ticket_id:UUID

class GetTicketOutput(BaseModel):
    ticket_id: UUID
    execution_id: UUID
    title: str
    category: str
    description: str
    proposed_fix: str
    priority: str
    status: str


class GetTicketFixInput(BaseModel):
    fix_id: UUID


class GetTicketFixOutput(BaseModel):
    fix_id: UUID
    ticket_id: UUID
    execution_id: UUID
    proposed_fix: str
    status: str

class DeleteTicketFixInput(BaseModel):
    fix_id: UUID


class DeleteTicketFixOutput(BaseModel):
    fix_id: UUID
    deleted: bool
