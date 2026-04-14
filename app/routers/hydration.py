"""Hydration tracking CRUD router."""

from fastapi import APIRouter, status, Query, Depends
from app.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import HydrationEntryCreate, HydrationEntryOut, HydrationEntryUpdate
from app.db import HydrationEntry, User
from app.database import get_session
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/hydration", tags=["Hydration Tracking"])


@router.post(
    "/",
    response_model=HydrationEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log a hydration entry",
)
async def create_hydration_entry(
    body: HydrationEntryCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    entry = HydrationEntry(
        owner_id=current_user.id,
        profile_id=body.profile_id,
        entry_date=str(body.entry_date),
        water_ml=body.water_ml,
        notes=body.notes,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)

    return HydrationEntryOut(
        id=entry.id,
        profile_id=entry.profile_id,
        entry_date=entry.entry_date,
        water_ml=entry.water_ml,
        notes=entry.notes,
    )


@router.get(
    "/",
    response_model=list[HydrationEntryOut],
    summary="List hydration entries",
)
async def list_hydration_entries(
    profile_id: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(HydrationEntry).where(HydrationEntry.owner_id == current_user.id)
    if profile_id:
        stmt = stmt.where(HydrationEntry.profile_id == profile_id)
    stmt = stmt.order_by(HydrationEntry.entry_date.desc()).offset(offset).limit(limit)

    result = await session.execute(stmt)
    entries = result.scalars().all()

    return [
        HydrationEntryOut(
            id=e.id,
            profile_id=e.profile_id,
            entry_date=e.entry_date,
            water_ml=e.water_ml,
            notes=e.notes,
        )
        for e in entries
    ]


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hydration entry",
)
async def delete_hydration_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(HydrationEntry).where(
        (HydrationEntry.id == entry_id) & (HydrationEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()

    if not entry:
        raise NotFoundError("Hydration entry not found")

    session.delete(entry)
    await session.commit()


@router.get(
    "/{entry_id}",
    response_model=HydrationEntryOut,
    summary="Get a hydration entry by ID",
)
async def get_hydration_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> HydrationEntryOut:
    stmt = select(HydrationEntry).where(
        (HydrationEntry.id == entry_id) & (HydrationEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Hydration entry not found")
    return HydrationEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        water_ml=entry.water_ml, notes=entry.notes,
    )


@router.put(
    "/{entry_id}",
    response_model=HydrationEntryOut,
    summary="Update a hydration entry",
)
async def update_hydration_entry(
    entry_id: str,
    body: HydrationEntryUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> HydrationEntryOut:
    stmt = select(HydrationEntry).where(
        (HydrationEntry.id == entry_id) & (HydrationEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Hydration entry not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(entry, field, str(value) if field == "entry_date" else value)

    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return HydrationEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        water_ml=entry.water_ml, notes=entry.notes,
    )
