"""Body metrics tracking CRUD router."""

from fastapi import APIRouter, status, Query, Depends
from app.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import BodyMetricEntryCreate, BodyMetricEntryOut, BodyMetricEntryUpdate
from app.db import BodyMetricEntry, User
from app.database import get_session
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/body-metrics", tags=["Body Metrics"])


@router.post(
    "/",
    response_model=BodyMetricEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log body metrics",
)
async def create_body_metric_entry(
    body: BodyMetricEntryCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    entry = BodyMetricEntry(
        owner_id=current_user.id,
        profile_id=body.profile_id,
        entry_date=str(body.entry_date),
        weight_kg=body.weight_kg,
        body_fat_pct=body.body_fat_pct,
        waist_cm=body.waist_cm,
        resting_hr=body.resting_hr,
        notes=body.notes,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)

    return BodyMetricEntryOut(
        id=entry.id,
        profile_id=entry.profile_id,
        entry_date=entry.entry_date,
        weight_kg=entry.weight_kg,
        body_fat_pct=entry.body_fat_pct,
        waist_cm=entry.waist_cm,
        resting_hr=entry.resting_hr,
        notes=entry.notes,
    )


@router.get(
    "/",
    response_model=list[BodyMetricEntryOut],
    summary="List body metric entries",
)
async def list_body_metric_entries(
    profile_id: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(BodyMetricEntry).where(BodyMetricEntry.owner_id == current_user.id)
    if profile_id:
        stmt = stmt.where(BodyMetricEntry.profile_id == profile_id)
    stmt = stmt.order_by(BodyMetricEntry.entry_date.desc()).offset(offset).limit(limit)

    result = await session.execute(stmt)
    entries = result.scalars().all()

    return [
        BodyMetricEntryOut(
            id=e.id,
            profile_id=e.profile_id,
            entry_date=e.entry_date,
            weight_kg=e.weight_kg,
            body_fat_pct=e.body_fat_pct,
            waist_cm=e.waist_cm,
            resting_hr=e.resting_hr,
            notes=e.notes,
        )
        for e in entries
    ]


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a body metric entry",
)
async def delete_body_metric_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(BodyMetricEntry).where(
        (BodyMetricEntry.id == entry_id) & (BodyMetricEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()

    if not entry:
        raise NotFoundError("Body metric entry not found")

    await session.delete(entry)
    await session.commit()


@router.get(
    "/{entry_id}",
    response_model=BodyMetricEntryOut,
    summary="Get a body metric entry by ID",
)
async def get_body_metric_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> BodyMetricEntryOut:
    stmt = select(BodyMetricEntry).where(
        (BodyMetricEntry.id == entry_id) & (BodyMetricEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Body metric entry not found")
    return BodyMetricEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        weight_kg=entry.weight_kg, body_fat_pct=entry.body_fat_pct,
        waist_cm=entry.waist_cm, resting_hr=entry.resting_hr, notes=entry.notes,
    )


@router.put(
    "/{entry_id}",
    response_model=BodyMetricEntryOut,
    summary="Update a body metric entry",
)
async def update_body_metric_entry(
    entry_id: str,
    body: BodyMetricEntryUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
) -> BodyMetricEntryOut:
    stmt = select(BodyMetricEntry).where(
        (BodyMetricEntry.id == entry_id) & (BodyMetricEntry.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    entry = result.scalars().first()
    if not entry:
        raise NotFoundError("Body metric entry not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(entry, field, str(value) if field == "entry_date" else value)

    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return BodyMetricEntryOut(
        id=entry.id, profile_id=entry.profile_id, entry_date=entry.entry_date,
        weight_kg=entry.weight_kg, body_fat_pct=entry.body_fat_pct,
        waist_cm=entry.waist_cm, resting_hr=entry.resting_hr, notes=entry.notes,
    )
