"""User account routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from starlette import status

from config import db_dependency
from exceptions import NotAuthorized
from models import Users
from schemas import UserVerification, UserResponse, ERROR_RESPONSES
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
    summary="Get current user profile",
    description="Retrieve the current authenticated user's profile information.",
)
async def get_current_user_info(user: user_dependency, db: db_dependency):
    """Get current user information."""
    if user is None:
        raise NotAuthorized()
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
    summary="Change user password",
    description="Update the current user's password. Requires current password verification.",
)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    """Change current user password."""
    if user is None:
        raise NotAuthorized()

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise NotAuthorized("Current password is incorrect")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
