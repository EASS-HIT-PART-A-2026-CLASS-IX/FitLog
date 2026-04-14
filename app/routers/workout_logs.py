"""Workout logs CRUD router with database persistence."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, status, Query, Depends
from app.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import WorkoutLogCreate, WorkoutLogOut, WorkoutLogUpdate
from app.db import WorkoutLog, User, Exercise
from app.database import get_session
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/logs", tags=["Workout Logs"])


@router.get("/", response_model=list[WorkoutLogOut], summary="List user's workout logs")
async def list_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    profile_id: Optional[str] = Query(
        None, description="Filter logs by fitness profile"
    ),
    start_date: Optional[date] = Query(
        None, description="Filter logs from this date (inclusive)"
    ),
    end_date: Optional[date] = Query(
        None, description="Filter logs until this date (inclusive)"
    ),
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    """List workout logs for the authenticated user with pagination and optional filtering.
    
    Args:
        limit: Max results per page (default 100)
        offset: Results offset for pagination (default 0)
        profile_id: Optional filter by fitness profile
        start_date: Optional filter from date (YYYY-MM-DD)
        end_date: Optional filter until date (YYYY-MM-DD)
        current_user: Authenticated user (from JWT)
        session: Database session
    
    Returns:
        List of WorkoutLogOut objects matching the filters
    """
    stmt = select(WorkoutLog).where(WorkoutLog.owner_id == current_user.id)

    if profile_id:
        stmt = stmt.where(WorkoutLog.profile_id == profile_id)
    if start_date:
        stmt = stmt.where(WorkoutLog.log_date >= str(start_date))
    if end_date:
        stmt = stmt.where(WorkoutLog.log_date <= str(end_date))

    stmt = stmt.order_by(WorkoutLog.log_date.desc()).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{log_id}", response_model=WorkoutLogOut, summary="Get a workout log by ID"
)
async def get_log(
    log_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific workout log (only if owned by user)."""
    stmt = select(WorkoutLog).where(
        (WorkoutLog.id == log_id) & (WorkoutLog.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    record = result.scalars().first()

    if not record:
        raise NotFoundError("Workout log not found")
    return record


@router.post(
    "/",
    response_model=WorkoutLogOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log a workout session",
)
async def create_log(
    body: WorkoutLogCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    """Create a new workout log for the authenticated user.
    
    Args:
        body: WorkoutLogCreate request (exercise_id, log_date, sets, reps, weight_kg, etc.)
              Note: log_date accepts both date objects and ISO strings (e.g., "2026-03-25")
        current_user: Authenticated user (from JWT)
        session: Database session
    
    Returns:
        WorkoutLogOut with created log ID and full details
    
    Raises:
        NotFoundError: If exercise not found or not owned by user
    """
    # Verify the exercise belongs to the user
    stmt = select(Exercise).where(
        (Exercise.id == str(body.exercise_id)) & (Exercise.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    exercise = result.scalars().first()

    if not exercise:
        raise NotFoundError("Exercise not found or not owned by user")

    # Prepare data for database (Pydantic validators already normalized types)
    log_data = body.model_dump()
    log_data["exercise_id"] = str(body.exercise_id)
    log_data["log_date"] = body.log_date.isoformat()
    log_data["owner_id"] = str(current_user.id)
    if body.profile_id:
        log_data["profile_id"] = str(body.profile_id)

    log = WorkoutLog(**log_data)
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


@router.put("/{log_id}", response_model=WorkoutLogOut, summary="Update a workout log")
async def update_log(
    log_id: str,
    body: WorkoutLogUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    """Update a workout log (only if owned by user)."""
    stmt = select(WorkoutLog).where(
        (WorkoutLog.id == log_id) & (WorkoutLog.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    record = result.scalars().first()

    if not record:
        raise NotFoundError("Workout log not found")

    # Update only provided fields (Pydantic validators already normalized types)
    update_data = body.model_dump(exclude_none=True)

    # Convert to database types if present
    if "exercise_id" in update_data and update_data["exercise_id"] is not None:
        update_data["exercise_id"] = str(update_data["exercise_id"])
    if "log_date" in update_data and update_data["log_date"] is not None:
        update_data["log_date"] = update_data["log_date"].isoformat()

    for key, value in update_data.items():
        setattr(record, key, value)

    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


@router.delete(
    "/{log_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a workout log"
)
async def delete_log(
    log_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session),
):
    """Delete a workout log (only if owned by user)."""
    stmt = select(WorkoutLog).where(
        (WorkoutLog.id == log_id) & (WorkoutLog.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    record = result.scalars().first()

    if not record:
        raise NotFoundError("Workout log not found")

    session.delete(record)
    await session.commit()
