"""User account routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from starlette import status

from config.db_dependencies import db_dependency
from config.settings import settings
from models import Users
from schemas import UserVerification
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(user: user_dependency, db: db_dependency):
    """Get current user information."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    """Change current user password."""
    if user is None:
        raise HTTPException(status_code=401, detail=settings.auth_failed_message)
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
