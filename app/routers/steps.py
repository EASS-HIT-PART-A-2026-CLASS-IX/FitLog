"""Daily step count tracking CRUD router."""

from fastapi import APIRouter, status, Query, Depends
from app.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import StepEntryCreate, StepEntryOut, StepEntryUpdate
from app.db import StepEntry, User
from app.database import get_session
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/steps", tags=["Step Tracking"])


@router.post(
    "/",
    response_model=StepEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log a step entry",
)
async def create_step_entry(
    body: StepEntryCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    entry = StepEntry(
        owner_id=current_user.id,
        profile_id=body.profile_id,
        entry_date=str(body.entry_date),
        steps=body.steps,
        distance_km=body.distance_km,
        active_minutes=body.active_minutes,
        notes=body.notes,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return StepEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        steps=entry.steps, distance_km=entry.distance_km,
        active_minutes=entry.active_minutes, notes=entry.notes,
    )


@router.get("/", response_model=list[StepEntryOut], summary="List step entries")
async def list_step_entries(
    profile_id: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(StepEntry).where(StepEntry.owner_id == current_user.id)
    if profile_id:
        stmt = stmt.where(StepEntry.profile_id == profile_id)
    stmt = stmt.order_by(StepEntry.entry_date.desc()).offset(offset).limit(limit)
    result = await session.execute(stmt)
    entries = result.scalars().all()
    return [
        StepEntryOut(
            id=e.id, profile_id=e.profile_id, entry_date=e.entry_date,
            steps=e.steps, distance_km=e.distance_km,
            active_minutes=e.active_minutes, notes=e.notes,
        )
        for e in entries
    ]


@router.get("/{entry_id}", response_model=StepEntryOut, summary="Get a step entry")
async def get_step_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(StepEntry).where(
        (StepEntry.id == entry_id) & (StepEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Step entry not found")
    return StepEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        steps=entry.steps, distance_km=entry.distance_km,
        active_minutes=entry.active_minutes, notes=entry.notes,
    )


@router.put("/{entry_id}", response_model=StepEntryOut, summary="Update a step entry")
async def update_step_entry(
    entry_id: str,
    body: StepEntryUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(StepEntry).where(
        (StepEntry.id == entry_id) & (StepEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Step entry not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(entry, field, str(value) if field == "entry_date" else value)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return StepEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        steps=entry.steps, distance_km=entry.distance_km,
        active_minutes=entry.active_minutes, notes=entry.notes,
    )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a step entry")
async def delete_step_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(StepEntry).where(
        (StepEntry.id == entry_id) & (StepEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Step entry not found")
    session.delete(entry)
    await session.commit()
