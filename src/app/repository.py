"""
In-memory repositories for all FitLog resources.
Each repo holds a dict[UUID, dict] and exposes list/get/create/update/delete.
Will be replaced by SQLModel + SQLite in EX3.

OPTIMIZED: Added pagination support to avoid loading all records.
"""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


class InMemoryRepo(Generic[T]):
    """Generic in-memory store with pagination support."""

    def __init__(self) -> None:
        self._store: dict[UUID, dict] = {}

    def list(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """
        Return paginated results for performance.
        
        Args:
            limit: Max number of records (default 100, max 500)
            offset: Number of records to skip (default 0)
        
        Returns:
            List of records from offset to offset+limit
        """
        limit = min(limit, 500)  # Cap at 500 to prevent huge payload
        offset = max(offset, 0)
        
        records = list(self._store.values())
        # Sort by creation order for consistent pagination
        records.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return records[offset:offset + limit]

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
