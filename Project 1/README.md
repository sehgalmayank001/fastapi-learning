# FastAPI Books API

A clean, well-architected FastAPI application for managing books with proper error handling and validation.

## Features

- **RESTful API** - Standard HTTP methods and resource-based URLs
- **Data Validation** - Pydantic models for request/response validation
- **Error Handling** - Centralized exception handling with consistent responses
- **API Documentation** - Auto-generated OpenAPI docs with ReDoc/Swagger
- **Clean Architecture** - Modular design with separation of concerns

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:

```bash
uvicorn books:app --reload
```

The API will be available at:

- **Application**: http://localhost:8000
- **Interactive docs (Swagger)**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

| Method   | Endpoint      | Description                             |
| -------- | ------------- | --------------------------------------- |
| `GET`    | `/books`      | Get all books (with optional filtering) |
| `GET`    | `/books/{id}` | Get book by ID                          |
| `POST`   | `/books`      | Create new book                         |
| `PUT`    | `/books/{id}` | Update book (full)                      |
| `PATCH`  | `/books/{id}` | Update book (partial)                   |
| `DELETE` | `/books/{id}` | Delete book                             |

### Query Parameters (GET /books)

- `category` - Filter by category
- `author` - Filter by author

### Examples

```bash
# Get all books
curl http://localhost:8000/books

# Filter by category
curl "http://localhost:8000/books?category=science"

# Get specific book
curl http://localhost:8000/books/1

# Create new book
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "author": "Author Name", "category": "fiction"}'

# Update book
curl -X PATCH "http://localhost:8000/books/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Delete book
curl -X DELETE http://localhost:8000/books/1
```

## Project Structure

```
Project 1/
├── books.py              # Main application and routes
├── api_response.py       # Response utilities
├── rescue.py            # Exception handling
├── models/              # Pydantic models
│   ├── book.py          # Book response model
│   ├── book_create.py   # Book creation model
│   ├── book_update.py   # Book update model
│   └── error_response.py # Error response model
├── exceptions/          # Custom exceptions
│   ├── api_exception.py # Base exception
│   ├── record_not_found.py
│   ├── record_invalid.py
│   └── ...
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Design Patterns

This project demonstrates several design patterns and clean code principles:

- **Chain of Responsibility** - Exception handling
- **Template Method** - Response formatting
- **Factory Method** - Exception creation
- **DTO Pattern** - Pydantic models
- **Single Responsibility** - Each module has one purpose

See `DESIGN_PATTERNS.md` for detailed documentation.

## Error Responses

All errors follow a consistent JSON structure:

```json
{
  "errors": {
    "message": "Book with identifier '123' not found"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Development

This is a learning project showcasing:

- Clean FastAPI architecture
- Proper error handling patterns
- Modular code organization
- RESTful API design
- Type safety with Pydantic
