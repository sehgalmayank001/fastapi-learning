"""Admin routes for privileged operations."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Path
from starlette import status

from config import db_dependency
from exceptions import NotAuthorized, RecordNotFound
from models import Todos
from schemas import TodoResponse, ValidId, ERROR_RESPONSES
from .auth import get_current_user


router = APIRouter(prefix="/admin", tags=["admin"])

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get(
    "/todos",
    response_model=List[TodoResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
    summary="Get all todos (admin only)",
    description="Retrieve all todos from all users. Requires admin privileges.",
)
async def get_all_todos(user: user_dependency, db: db_dependency):
    """Get all todos (admin only)."""
    if user is None:
        raise NotAuthorized()
    if user.get("user_role") != "admin":
        raise NotAuthorized("Admin access required")
    return db.query(Todos).all()


@router.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
    summary="Delete any todo (admin only)",
    description="Delete any todo by ID regardless of owner. Requires admin privileges.",
)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: ValidId):
    """Delete any todo by ID (admin only)."""
    if user is None:
        raise NotAuthorized()
    if user.get("user_role") != "admin":
        raise NotAuthorized("Admin access required")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise RecordNotFound("Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
