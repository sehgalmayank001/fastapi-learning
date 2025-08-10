"""Admin routes for privileged operations."""

from typing import Annotated
from config.db_dependencies import db_dependency
from config.settings import settings
from models import Todos

from starlette import status
from fastapi import APIRouter, Depends, HTTPException, Path
from .auth import get_current_user


router = APIRouter(prefix="/admin", tags=["admin"])

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    """Get all todos (admin only)."""
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)
    return db.query(Todos).all()


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    """Delete any todo by ID (admin only)."""
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=settings.record_not_found_message)
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
