"""Book update model."""

from typing import Optional
from pydantic import BaseModel


class BookUpdate(BaseModel):
    """Model for book update requests - all fields optional for PATCH."""

    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
