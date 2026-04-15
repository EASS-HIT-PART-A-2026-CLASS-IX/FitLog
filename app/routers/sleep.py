"""Sleep tracking CRUD router."""

from fastapi import APIRouter, status, Query, Depends
from app.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import SleepEntryCreate, SleepEntryOut, SleepEntryUpdate
from app.db import SleepEntry, User
from app.database import get_session
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/sleep", tags=["Sleep Tracking"])


@router.post(
    "/",
    response_model=SleepEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log a sleep entry",
)
async def create_sleep_entry(
    body: SleepEntryCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    entry = SleepEntry(
        owner_id=current_user.id,
        profile_id=body.profile_id,
        entry_date=str(body.entry_date),
        sleep_hours=body.sleep_hours,
        sleep_quality=body.sleep_quality,
        notes=body.notes,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)

    return SleepEntryOut(
        id=entry.id,
        profile_id=entry.profile_id,
        entry_date=entry.entry_date,
        sleep_hours=entry.sleep_hours,
        sleep_quality=entry.sleep_quality,
        notes=entry.notes,
    )


@router.get(
    "/",
    response_model=list[SleepEntryOut],
    summary="List sleep entries",
)
async def list_sleep_entries(
    profile_id: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(SleepEntry).where(SleepEntry.owner_id == current_user.id)
    if profile_id:
        stmt = stmt.where(SleepEntry.profile_id == profile_id)
    stmt = stmt.order_by(SleepEntry.entry_date.desc()).offset(offset).limit(limit)

    result = await session.execute(stmt)
    entries = result.scalars().all()

    return [
        SleepEntryOut(
            id=e.id,
            profile_id=e.profile_id,
            entry_date=e.entry_date,
            sleep_hours=e.sleep_hours,
            sleep_quality=e.sleep_quality,
            notes=e.notes,
        )
        for e in entries
    ]


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sleep entry",
)
async def delete_sleep_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(SleepEntry).where(
        (SleepEntry.id == entry_id) & (SleepEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()

    if not entry:
        raise NotFoundError("Sleep entry not found")

    await session.delete(entry)
    await session.commit()


@router.get(
    "/{entry_id}",
    response_model=SleepEntryOut,
    summary="Get a sleep entry by ID",
)
async def get_sleep_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> SleepEntryOut:
    stmt = select(SleepEntry).where(
        (SleepEntry.id == entry_id) & (SleepEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Sleep entry not found")
    return SleepEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        sleep_hours=entry.sleep_hours, sleep_quality=entry.sleep_quality, notes=entry.notes,
    )


@router.put(
    "/{entry_id}",
    response_model=SleepEntryOut,
    summary="Update a sleep entry",
)
async def update_sleep_entry(
    entry_id: str,
    body: SleepEntryUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> SleepEntryOut:
    stmt = select(SleepEntry).where(
        (SleepEntry.id == entry_id) & (SleepEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Sleep entry not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(entry, field, str(value) if field == "entry_date" else value)

    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return SleepEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        sleep_hours=entry.sleep_hours, sleep_quality=entry.sleep_quality, notes=entry.notes,
    )
