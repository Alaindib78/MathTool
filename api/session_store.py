from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4

from core.engine import MathToolSession


@dataclass
class StoredSession:
    id: str
    session: MathToolSession
    created_at: datetime
    updated_at: datetime
    lock: RLock = field(default_factory=RLock)

    def touch(self):
        self.updated_at = utc_now()


class SessionStore:
    def __init__(self):
        self._sessions = {}
        self._lock = RLock()

    def create(self):
        session_id = str(uuid4())
        now = utc_now()

        stored_session = StoredSession(
            id=session_id,
            session=MathToolSession(),
            created_at=now,
            updated_at=now,
        )

        with self._lock:
            self._sessions[session_id] = stored_session

        return stored_session

    def get(self, session_id):
        with self._lock:
            stored_session = self._sessions.get(
                session_id
            )

        if stored_session is None:
            raise KeyError(session_id)

        stored_session.touch()
        return stored_session

    def delete(self, session_id):
        with self._lock:
            return (
                self._sessions.pop(session_id, None)
                is not None
            )

    def list(self):
        with self._lock:
            return list(self._sessions.values())

    def clear(self):
        with self._lock:
            self._sessions.clear()


def utc_now():
    return datetime.now(timezone.utc)
