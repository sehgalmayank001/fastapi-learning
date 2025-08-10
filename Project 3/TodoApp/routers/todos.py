"""Todo CRUD routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status

from config.db_dependencies import db_dependency
from config.settings import settings
from models import Todos
from .auth import get_current_user

router = APIRouter()


user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    """Request model for todo operations."""

    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    """Get all todos for the current user."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    """Get a specific todo by ID."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)

    todo_model = (
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=settings.record_not_found_message)


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    """Create a new todo."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    """Update an existing todo."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)

    todo_model = (
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail=settings.record_not_found_message)

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    """Delete a todo."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)

    todo_model = (
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail=settings.record_not_found_message)
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()

    db.commit()
