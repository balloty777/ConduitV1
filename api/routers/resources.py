from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from database.models.marketing_content import MarketingContent
from database.models.sales_follow_ups import SalesFollowUp
from database.models.sales_lead import SalesLead
from database.models.tech_fix import TechFix
from database.models.tech_ticket import TechTicket

router = APIRouter(tags=["Resources"])


def _content(row: MarketingContent) -> dict:
    return {"content_id": str(row.id), "execution_id": str(row.execution_id), "platform": row.platform,
            "content": row.content, "tone": row.tone, "audience": row.audience,
            "call_to_action": row.call_to_action, "status": row.status,
            "scheduled_at": row.scheduled_at, "created_at": row.created_at, "updated_at": row.updated_at}


def _lead(row: SalesLead) -> dict:
    return {"lead_id": str(row.id), "execution_id": str(row.execution_id), "name": row.name,
            "email": row.email, "phone": row.phone, "status": row.status,
            "created_at": row.created_at, "updated_at": row.updated_at}


def _follow_up(row: SalesFollowUp) -> dict:
    return {"follow_up_id": str(row.id), "lead_id": str(row.lead_id), "execution_id": str(row.execution_id),
            "message": row.message, "channel": row.channel, "status": row.status,
            "scheduled_at": row.scheduled_at, "created_at": row.created_at, "updated_at": row.updated_at}


def _ticket(row: TechTicket) -> dict:
    return {"ticket_id": str(row.id), "execution_id": str(row.execution_id), "title": row.title,
            "category": row.category, "description": row.description, "proposed_fix": row.proposed_fix,
            "priority": row.priority, "status": row.status, "created_at": row.created_at,
            "updated_at": row.updated_at}


def _fix(row: TechFix) -> dict:
    return {"fix_id": str(row.id), "ticket_id": str(row.ticket_id), "execution_id": str(row.execution_id),
            "proposed_fix": row.proposed_fix, "status": row.status, "created_at": row.created_at,
            "updated_at": row.updated_at}


def _one(db: Session, model, object_id: UUID, label: str):
    row = db.get(model, object_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return row


@router.get("/marketing/content")
def list_marketing_content(db: Session = Depends(get_db)):
    rows = db.query(MarketingContent).order_by(MarketingContent.created_at.desc()).limit(500).all()
    return [_content(row) for row in rows]


@router.get("/sales/leads")
def list_leads(db: Session = Depends(get_db)):
    rows = db.query(SalesLead).order_by(SalesLead.created_at.desc()).limit(500).all()
    return [_lead(row) for row in rows]


@router.get("/sales/leads/{lead_id}")
def get_lead(lead_id: UUID, db: Session = Depends(get_db)):
    return _lead(_one(db, SalesLead, lead_id, "Lead"))


@router.get("/sales/follow-ups")
def list_follow_ups(db: Session = Depends(get_db)):
    rows = db.query(SalesFollowUp).order_by(SalesFollowUp.created_at.desc()).limit(500).all()
    return [_follow_up(row) for row in rows]


@router.get("/sales/follow-ups/{follow_up_id}")
def get_follow_up(follow_up_id: UUID, db: Session = Depends(get_db)):
    return _follow_up(_one(db, SalesFollowUp, follow_up_id, "Follow-up"))


@router.get("/tech/tickets")
def list_tickets(db: Session = Depends(get_db)):
    rows = db.query(TechTicket).order_by(TechTicket.created_at.desc()).limit(500).all()
    return [_ticket(row) for row in rows]


@router.get("/tech/tickets/{ticket_id}")
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    return _ticket(_one(db, TechTicket, ticket_id, "Ticket"))


@router.get("/tech/fixes")
def list_fixes(db: Session = Depends(get_db)):
    rows = db.query(TechFix).order_by(TechFix.created_at.desc()).limit(500).all()
    return [_fix(row) for row in rows]


@router.get("/tech/fixes/{fix_id}")
def get_fix(fix_id: UUID, db: Session = Depends(get_db)):
    return _fix(_one(db, TechFix, fix_id, "Fix"))
