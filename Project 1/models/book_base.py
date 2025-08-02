"""Base book model."""

from pydantic import BaseModel


class BookBase(BaseModel):
    """Base book fields shared across models."""

    title: str
    author: str
    category: str
