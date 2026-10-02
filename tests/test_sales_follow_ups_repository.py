from unittest.mock import Mock
from uuid import uuid4

from database.models.sales_follow_ups import SalesFollowUp
from database.repositories.sales_follow_ups_repository import SalesFollowUpsRepository


def test_create_follow_up_adds_and_flushes():
    db = Mock()
    repository = SalesFollowUpsRepository(db)
    follow_up = Mock(spec=SalesFollowUp)
    result = repository.create(follow_up)
    assert result is follow_up
    db.add.assert_called_once_with(follow_up)
    db.flush.assert_called_once()


def test_get_by_id_returns_follow_up():
    db = Mock()
    repository = SalesFollowUpsRepository(db)
    follow_up_id = uuid4()
    follow_up = Mock(spec=SalesFollowUp)
    db.get.return_value = follow_up
    result = repository.get_by_id(follow_up_id)
    assert result is follow_up
    db.get.assert_called_once_with(SalesFollowUp, follow_up_id)


def test_update_flushes_and_returns_follow_up():
    db = Mock()
    repository = SalesFollowUpsRepository(db)
    follow_up = Mock(spec=SalesFollowUp)
    result = repository.update(follow_up)
    assert result is follow_up
    db.flush.assert_called_once()

def test_delete_follow_up_deletes_and_flushes():
    db = Mock()
    repository = SalesFollowUpsRepository(db)
    follow_up_id = uuid4()
    follow_up = Mock(spec=SalesFollowUp)
    db.get.return_value = follow_up
    result = repository.delete(follow_up_id)
    assert result is None
    db.get.assert_called_once_with(SalesFollowUp, follow_up_id)
    db.delete.assert_called_once_with(follow_up)
    db.flush.assert_called_once()

def test_delete_missing_follow_up_does_nothing():
    db = Mock()
    repository = SalesFollowUpsRepository(db)
    follow_up_id = uuid4()
    db.get.return_value = None
    result = repository.delete(follow_up_id)
    assert result is None
    db.get.assert_called_once_with(SalesFollowUp, follow_up_id)
    db.delete.assert_not_called()
    db.flush.assert_not_called()