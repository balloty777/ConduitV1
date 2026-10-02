from unittest.mock import Mock
from uuid import uuid4
from database.models.sales_lead import SalesLead
from database.repositories.sales_lead_repository import SalesLeadRepository

def test_get_by_execution_id_queries_execution_id():
    db = Mock()
    repository = SalesLeadRepository(db)
    execution_id = uuid4()
    lead = Mock()
    query = Mock()
    filtered_query = Mock()
    db.query.return_value = query
    query.filter.return_value = filtered_query
    filtered_query.first.return_value = lead
    result = repository.get_by_execution_id(execution_id)
    assert result is lead
    db.query.assert_called_once_with(SalesLead)
    filter_expression = query.filter.call_args.args[0]
    assert filter_expression.left == SalesLead.execution_id
    assert filter_expression.right.value == execution_id
    filtered_query.first.assert_called_once()