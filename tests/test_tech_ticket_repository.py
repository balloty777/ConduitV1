from unittest.mock import Mock
from uuid import uuid4
from database.models.tech_ticket import TechTicket
from database.repositories.tech_ticket_repository import TechTicketRepository

def test_delete_flushes_deleted_ticket():
    db = Mock()
    repository = TechTicketRepository(db)
    ticket_id = uuid4()
    ticket = Mock(spec=TechTicket)
    ticket.id = ticket_id
    db.get.return_value = ticket
    result = repository.delete(ticket_id)
    assert result is None
    db.get.assert_called_once_with(TechTicket, ticket_id)
    db.delete.assert_called_once_with(ticket)
    db.flush.assert_called_once()


def test_delete_missing_ticket_does_not_delete_or_flush():
    db = Mock()
    repository = TechTicketRepository(db)
    ticket_id = uuid4()
    db.get.return_value = None
    result = repository.delete(ticket_id)
    assert result is None
    db.get.assert_called_once_with(TechTicket, ticket_id)
    db.delete.assert_not_called()
    db.flush.assert_not_called()