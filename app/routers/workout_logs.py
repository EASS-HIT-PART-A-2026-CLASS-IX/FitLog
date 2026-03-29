"""Workout logs CRUD router with database persistence."""
from fastapi import APIRouter, HTTPException, status, Query, Depends
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
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session)
):
    """List workout logs for the authenticated user with pagination."""
    stmt = select(WorkoutLog).where(WorkoutLog.owner_id == current_user.id).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{log_id}", response_model=WorkoutLogOut, summary="Get a workout log by ID")
async def get_log(
    log_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific workout log (only if owned by user)."""
    stmt = select(WorkoutLog).where(
        (WorkoutLog.id == log_id) & (WorkoutLog.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    return record


@router.post("/", response_model=WorkoutLogOut, status_code=status.HTTP_201_CREATED, summary="Log a workout session")
async def create_log(
    body: WorkoutLogCreate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session)
):
    """Create a new workout log for the authenticated user."""
    # Verify the exercise belongs to the user
    stmt = select(Exercise).where(
        (Exercise.id == body.exercise_id) & (Exercise.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    exercise = result.scalars().first()
    
    if not exercise:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exercise not found or not owned by user")
    
    log = WorkoutLog(
        **body.model_dump(),
        owner_id=current_user.id
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


@router.put("/{log_id}", response_model=WorkoutLogOut, summary="Update a workout log")
async def update_log(
    log_id: str,
    body: WorkoutLogUpdate,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session)
):
    """Update a workout log (only if owned by user)."""
    stmt = select(WorkoutLog).where(
        (WorkoutLog.id == log_id) & (WorkoutLog.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    # Update only provided fields
    update_data = body.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a workout log")
async def delete_log(
    log_id: str,
    current_user: User = Depends(get_current_user_from_header),
    session: AsyncSession = Depends(get_session)
):
    """Delete a workout log (only if owned by user)."""
    stmt = select(WorkoutLog).where(
        (WorkoutLog.id == log_id) & (WorkoutLog.owner_id == current_user.id)
    )
    result = await session.execute(stmt)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    await session.delete(record)
    await session.commit()
