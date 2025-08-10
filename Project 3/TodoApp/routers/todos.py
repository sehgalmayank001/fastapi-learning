"""Todo CRUD routes."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Path
from starlette import status

from config import db_dependency
from exceptions import NotAuthorized, RecordNotFound
from models import Todos
from schemas import TodoRequest, TodoResponse, ValidId, ERROR_RESPONSES
from .auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

# Using shared components from config.api_docs

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get(
    "/",
    response_model=List[TodoResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def get_todos(user: user_dependency, db: db_dependency):
    """Get all todos for the current user."""
    if user is None:
        raise NotAuthorized()
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: ValidId):
    """Get a specific todo by ID."""
    if user is None:
        raise NotAuthorized()

    todo_model = (
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    )
    if todo_model is not None:
        return todo_model
    raise RecordNotFound("Todo not found")


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    """Create a new todo."""
    if user is None:
        raise NotAuthorized()
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: ValidId,
):
    """Update an existing todo."""
    if user is None:
        raise NotAuthorized()

    todo_model = (
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    )
    if todo_model is None:
        raise RecordNotFound("Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: ValidId):
    """Delete a todo."""
    if user is None:
        raise NotAuthorized()

    todo_model = (
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    )
    if todo_model is None:
        raise RecordNotFound("Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()

    db.commit()
