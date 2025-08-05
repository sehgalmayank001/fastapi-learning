"""FastAPI application for managing books."""

from typing import List, Optional, Annotated

from exceptions import RecordNotFound
from models import Book, BookCreate, BookUpdate, ErrorResponse
from rescue import setup_exception_handlers
from fastapi import FastAPI, Path, status as http_status
from fastapi.responses import Response

app = FastAPI()

# Reusable path parameter with validation - DRY approach
ValidBookId = Annotated[int, Path(gt=0, description="Book ID must be greater than 0")]

# Common error responses for documentation
ERROR_RESPONSES = {404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}
VALIDATION_RESPONSES = {422: {"model": ErrorResponse}}

# Setup Rails-style exception handlers
setup_exception_handlers(app)


BOOKS = [
    {"id": 1, "title": "Title One", "author": "Author One", "category": "science"},
    {"id": 2, "title": "Title Two", "author": "Author Two", "category": "science"},
    {"id": 3, "title": "Title Three", "author": "Author Three", "category": "history"},
    {"id": 4, "title": "Title Four", "author": "Author Four", "category": "math"},
    {"id": 5, "title": "Title Five", "author": "Author Five", "category": "math"},
    {"id": 6, "title": "Title Six", "author": "Author Two", "category": "math"},
]


@app.get(
    "/books",
    response_model=List[Book],
    status_code=http_status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def index(category: Optional[str] = None, author: Optional[str] = None):
    """Return all books, optionally filtered by category and/or author."""
    filtered_books = BOOKS

    if category:
        filtered_books = [
            book
            for book in filtered_books
            if book.get("category", "").casefold() == category.casefold()
        ]

    if author:
        filtered_books = [
            book
            for book in filtered_books
            if book.get("author", "").casefold() == author.casefold()
        ]

    return filtered_books


@app.get(
    "/books/{book_id}",
    response_model=Book,
    status_code=http_status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def show(book_id: ValidBookId):
    """Return a specific book by ID."""
    for book in BOOKS:
        if book.get("id") == book_id:
            return book
    raise RecordNotFound("Book", book_id)


@app.post(
    "/books",
    response_model=Book,
    status_code=http_status.HTTP_201_CREATED,
    responses=VALIDATION_RESPONSES,
)
async def create(new_book: BookCreate):
    """Create a new book."""
    # Generate new ID
    new_id = max((book["id"] for book in BOOKS), default=0) + 1
    book_dict = new_book.model_dump()
    book_dict["id"] = new_id
    BOOKS.append(book_dict)
    return book_dict


@app.put(
    "/books/{book_id}",
    response_model=Book,
    status_code=http_status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
@app.patch(
    "/books/{book_id}",
    response_model=Book,
    status_code=http_status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def update(book_id: ValidBookId, updates: BookUpdate):
    """Update an existing book (supports both PUT and PATCH)."""
    for i, book in enumerate(BOOKS):
        if book.get("id") == book_id:
            # Update only provided fields
            update_data = updates.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key != "id":  # Don't allow ID changes
                    book[key] = value
            BOOKS[i] = book
            return book
    raise RecordNotFound("Book", book_id)


@app.delete(
    "/books/{book_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
async def destroy(book_id: ValidBookId):
    """Delete a book by ID."""
    for i, book in enumerate(BOOKS):
        if book.get("id") == book_id:
            BOOKS.pop(i)
            return Response(status_code=http_status.HTTP_204_NO_CONTENT)
    raise RecordNotFound("Book", book_id)
