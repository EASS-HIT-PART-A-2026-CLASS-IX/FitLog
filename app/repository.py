"""
In-memory repositories for all FitLog resources.
Each repo holds a dict[UUID, dict] and exposes list/get/create/update/delete.
Will be replaced by SQLModel + SQLite in EX3.
"""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


class InMemoryRepo(Generic[T]):
    """Generic in-memory store."""

    def __init__(self) -> None:
        self._store: dict[UUID, dict] = {}

    def list(self) -> list[dict]:
        return list(self._store.values())

    def get(self, id: UUID) -> dict | None:
        return self._store.get(id)

    def create(self, data: dict) -> dict:
        id = uuid4()
        record = {"id": id, **data}
        self._store[id] = record
        return record

    def update(self, id: UUID, data: dict) -> dict | None:
        record = self._store.get(id)
        if record is None:
            return None
        # Only update fields that are explicitly provided (not None)
        for key, value in data.items():
            if value is not None:
                record[key] = value
        return record

    def delete(self, id: UUID) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True


# Singleton repos — shared across requests within a process
exercises_repo: InMemoryRepo = InMemoryRepo()
workout_logs_repo: InMemoryRepo = InMemoryRepo()
macros_repo: InMemoryRepo = InMemoryRepo()
profiles_repo: InMemoryRepo = InMemoryRepo()
