from unittest.mock import Mock
from uuid import uuid4
from database.models.marketing_content import MarketingContent
from database.repositories.marketing_content_repository import MarketingContentRepository


def test_get_by_execution_id_queries_execution_id():
    db = Mock()
    repository = MarketingContentRepository(db)
    execution_id = uuid4()
    content = Mock()
    query = Mock()
    filtered_query = Mock()
    db.query.return_value = query
    query.filter.return_value = filtered_query
    filtered_query.first.return_value = content
    result = repository.get_by_execution_id(execution_id)
    assert result is content
    db.query.assert_called_once_with(MarketingContent)
    filter_expression = query.filter.call_args.args[0]
    assert filter_expression.left == MarketingContent.execution_id
    assert filter_expression.right.value == execution_id
    filtered_query.first.assert_called_once()