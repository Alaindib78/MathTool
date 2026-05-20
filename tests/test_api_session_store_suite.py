import pytest

from api.session_store import SessionStore


def test_session_store_creates_and_retrieves_sessions():
    store = SessionStore()

    stored = store.create()
    retrieved = store.get(stored.id)

    assert retrieved is stored
    assert retrieved.session.context is stored.session.context


def test_session_store_raises_for_missing_session():
    store = SessionStore()

    with pytest.raises(KeyError):
        store.get("missing")


def test_session_store_deletes_sessions():
    store = SessionStore()
    stored = store.create()

    assert store.delete(stored.id) is True
    assert store.delete(stored.id) is False

    with pytest.raises(KeyError):
        store.get(stored.id)
