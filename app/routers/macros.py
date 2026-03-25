"""Macro / nutrition entries CRUD router."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models import MacroEntryCreate, MacroEntryOut, MacroEntryUpdate
from app.repository import macros_repo

router = APIRouter(prefix="/macros", tags=["Macro Entries"])


@router.get("/", response_model=list[MacroEntryOut], summary="List all macro entries")
def list_macros():
    return macros_repo.list()


@router.get("/{entry_id}", response_model=MacroEntryOut, summary="Get a macro entry by ID")
def get_macro(entry_id: UUID):
    record = macros_repo.get(entry_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Macro entry not found")
    return record


@router.post("/", response_model=MacroEntryOut, status_code=status.HTTP_201_CREATED, summary="Log daily macros")
def create_macro(body: MacroEntryCreate):
    return macros_repo.create(body.model_dump())


@router.put("/{entry_id}", response_model=MacroEntryOut, summary="Update a macro entry")
def update_macro(entry_id: UUID, body: MacroEntryUpdate):
    updated = macros_repo.update(entry_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Macro entry not found")
    return updated


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a macro entry")
def delete_macro(entry_id: UUID):
    if not macros_repo.delete(entry_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Macro entry not found")
