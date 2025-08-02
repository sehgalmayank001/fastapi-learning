"""Book response model."""

from pydantic import BaseModel


class Book(BaseModel):
    """Model for book responses with ID."""

    id: int
    title: str
    author: str
    category: str

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration."""

        from_attributes = True
