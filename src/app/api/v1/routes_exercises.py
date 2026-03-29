"""Exercises CRUD router."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query

from src.app.schemas import ExerciseCreate, ExerciseOut, ExerciseUpdate
from app.repository import exercises_repo

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("/", response_model=list[ExerciseOut], summary="List all exercises")
def list_exercises(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List exercises with pagination. Default 100 per page, max 500."""
    return exercises_repo.list(limit=limit, offset=offset)


@router.get("/{exercise_id}", response_model=ExerciseOut, summary="Get an exercise by ID")
def get_exercise(exercise_id: UUID):
    record = exercises_repo.get(exercise_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return record


@router.post("/", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED, summary="Create a new exercise")
def create_exercise(body: ExerciseCreate):
    return exercises_repo.create(body.model_dump())


@router.put("/{exercise_id}", response_model=ExerciseOut, summary="Update an exercise")
def update_exercise(exercise_id: UUID, body: ExerciseUpdate):
    updated = exercises_repo.update(exercise_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return updated


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an exercise")
def delete_exercise(exercise_id: UUID):
    if not exercises_repo.delete(exercise_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
