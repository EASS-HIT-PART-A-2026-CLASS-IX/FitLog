"""Recovery tracking CRUD router."""

from fastapi import APIRouter, status, Query, Depends
from app.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import RecoveryEntryCreate, RecoveryEntryOut, RecoveryEntryUpdate
from app.db import RecoveryEntry, User
from app.database import get_session
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/recovery", tags=["Recovery Tracking"])


@router.post(
    "/",
    response_model=RecoveryEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log a recovery entry",
)
async def create_recovery_entry(
    body: RecoveryEntryCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    entry = RecoveryEntry(
        owner_id=current_user.id,
        profile_id=body.profile_id,
        entry_date=str(body.entry_date),
        soreness_level=body.soreness_level,
        energy_level=body.energy_level,
        stress_level=body.stress_level,
        mood=body.mood,
        notes=body.notes,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)

    return RecoveryEntryOut(
        id=entry.id,
        profile_id=entry.profile_id,
        entry_date=entry.entry_date,
        soreness_level=entry.soreness_level,
        energy_level=entry.energy_level,
        stress_level=entry.stress_level,
        mood=entry.mood,
        notes=entry.notes,
    )


@router.get(
    "/",
    response_model=list[RecoveryEntryOut],
    summary="List recovery entries",
)
async def list_recovery_entries(
    profile_id: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(RecoveryEntry).where(RecoveryEntry.owner_id == current_user.id)
    if profile_id:
        stmt = stmt.where(RecoveryEntry.profile_id == profile_id)
    stmt = stmt.order_by(RecoveryEntry.entry_date.desc()).offset(offset).limit(limit)

    result = await session.execute(stmt)
    entries = result.scalars().all()

    return [
        RecoveryEntryOut(
            id=e.id,
            profile_id=e.profile_id,
            entry_date=e.entry_date,
            soreness_level=e.soreness_level,
            energy_level=e.energy_level,
            stress_level=e.stress_level,
            mood=e.mood,
            notes=e.notes,
        )
        for e in entries
    ]


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recovery entry",
)
async def delete_recovery_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(RecoveryEntry).where(
        (RecoveryEntry.id == entry_id) & (RecoveryEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()

    if not entry:
        raise NotFoundError("Recovery entry not found")

    session.delete(entry)
    await session.commit()


@router.get(
    "/{entry_id}",
    response_model=RecoveryEntryOut,
    summary="Get a recovery entry by ID",
)
async def get_recovery_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> RecoveryEntryOut:
    stmt = select(RecoveryEntry).where(
        (RecoveryEntry.id == entry_id) & (RecoveryEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Recovery entry not found")
    return RecoveryEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        soreness_level=entry.soreness_level, energy_level=entry.energy_level,
        stress_level=entry.stress_level, mood=entry.mood, notes=entry.notes,
    )


@router.put(
    "/{entry_id}",
    response_model=RecoveryEntryOut,
    summary="Update a recovery entry",
)
async def update_recovery_entry(
    entry_id: str,
    body: RecoveryEntryUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> RecoveryEntryOut:
    stmt = select(RecoveryEntry).where(
        (RecoveryEntry.id == entry_id) & (RecoveryEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Recovery entry not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(entry, field, str(value) if field == "entry_date" else value)

    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return RecoveryEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        soreness_level=entry.soreness_level, energy_level=entry.energy_level,
        stress_level=entry.stress_level, mood=entry.mood, notes=entry.notes,
    )
