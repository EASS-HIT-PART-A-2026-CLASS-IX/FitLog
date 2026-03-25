"""Workout logs CRUD router."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models import WorkoutLogCreate, WorkoutLogOut, WorkoutLogUpdate
from app.repository import workout_logs_repo

router = APIRouter(prefix="/logs", tags=["Workout Logs"])


@router.get("/", response_model=list[WorkoutLogOut], summary="List all workout logs")
def list_logs():
    return workout_logs_repo.list()


@router.get("/{log_id}", response_model=WorkoutLogOut, summary="Get a workout log by ID")
def get_log(log_id: UUID):
    record = workout_logs_repo.get(log_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    return record


@router.post("/", response_model=WorkoutLogOut, status_code=status.HTTP_201_CREATED, summary="Log a workout session")
def create_log(body: WorkoutLogCreate):
    return workout_logs_repo.create(body.model_dump())


@router.put("/{log_id}", response_model=WorkoutLogOut, summary="Update a workout log")
def update_log(log_id: UUID, body: WorkoutLogUpdate):
    updated = workout_logs_repo.update(log_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    return updated


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a workout log")
def delete_log(log_id: UUID):
    if not workout_logs_repo.delete(log_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
