# Design Patterns & Principles Implemented

This document outlines the design patterns, principles, and refactoring techniques applied to transform a monolithic FastAPI application into a clean, maintainable codebase.

## 🏗️ Design Patterns

### 1. Chain of Responsibility Pattern

**Location:** `rescue.py` - Exception handlers

The exception handling system forms a chain where each handler is responsible for specific exception types.

```python
@app.exception_handler(RecordNotFound)      # Handler 1
@app.exception_handler(RecordInvalid)       # Handler 2
@app.exception_handler(RequestValidationError) # Handler 3
@app.exception_handler(ValueError)          # Handler 4
@app.exception_handler(Exception)           # Catch-all handler
```

**Benefits:**

- Decouples senders from receivers
- Easy to add/remove handlers
- Clear responsibility separation

### 2. Template Method Pattern

**Location:** `api_response.py` - Response formatting

The `json_response` function defines a template for all API responses with consistent structure.

```python
def json_response(data: Dict[str, Any], status: int = 200, options: Dict = None):
    # Template structure for all responses
    response_data = {
        **data,  # Variable content
        "timestamp": datetime.now(timezone.utc).isoformat()  # Fixed template part
    }
    return JSONResponse(content=response_data, status_code=status)
```

**Benefits:**

- Consistent response format across entire API
- Easy to modify global response structure
- Eliminates duplicate formatting code

### 3. Factory Method Pattern

**Location:** `exceptions/` - Exception creation

Each exception class acts as a factory for creating standardized error objects.

```python
class RecordNotFound(APIException):
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"  # Factory logic
        super().__init__(message, 404)

# Usage: RecordNotFound("Book", 123) creates standardized error
```

**Benefits:**

- Encapsulates object creation logic
- Ensures consistent error messages
- Easy to extend with new exception types

### 4. Data Transfer Object (DTO) Pattern

**Location:** `models/` - Request/response models

Pydantic models serve as DTOs that handle data validation and serialization.

```python
class BookCreate(BaseModel):    # Request DTO
    title: str
    author: str
    category: str

class Book(BaseModel):          # Response DTO
    id: int
    title: str
    author: str
    category: str
```

**Benefits:**

- Automatic validation of incoming data
- Consistent serialization of outgoing data
- Type safety and IDE support
- Self-documenting API schemas

### 5. Facade Pattern

**Location:** `rescue.py` - Exception handling setup

The `setup_exception_handlers` function provides a simple interface to complex exception handling configuration.

```python
def setup_exception_handlers(app: FastAPI):
    """Facade that hides complex exception handler setup"""
    # Complex internal setup hidden behind simple interface
    @app.exception_handler(RecordNotFound)
    # ... multiple handlers

# Simple usage in main app:
setup_exception_handlers(app)  # One line configures everything
```

**Benefits:**

- Simplifies complex subsystem interaction
- Provides clean interface for main application
- Hides implementation details

## 🎯 SOLID Principles Applied

### Single Responsibility Principle (SRP)

Each module has one clear responsibility:

- `books.py` - HTTP route handling and business logic
- `api_response.py` - Response formatting
- `rescue.py` - Exception handling
- `exceptions/` - Exception definitions
- `models/` - Data transfer objects (Pydantic models)

### Open/Closed Principle (OCP)

The system is open for extension, closed for modification:

```python
# Adding new exception type doesn't require changing existing code
class BookExpired(APIException):  # New exception
    def __init__(self, book_id: int):
        super().__init__(f"Book {book_id} has expired", 410)

# Add handler without modifying existing handlers
@app.exception_handler(BookExpired)
async def handle_book_expired(_request, exc):
    return json_response({"errors": {"message": exc.message}}, status=exc.status_code)
```

### Dependency Inversion Principle (DIP)

High-level modules don't depend on low-level modules:

```python
# High-level module (books.py) depends on abstraction
from api_response import json_response  # Abstraction
from exceptions import RecordNotFound   # Abstraction

# Not directly on concrete implementations
```

## 🔧 Refactoring Techniques Used

### 0. Remove Unnecessary Abstraction

**Applied to:** BookBase class removal

**Before:** Abstract base class for 3 simple fields

```python
class BookBase(BaseModel):
    title: str
    author: str
    category: str

class Book(BookBase):
    id: int
```

**After:** Direct, explicit models

```python
class Book(BaseModel):
    id: int
    title: str
    author: str
    category: str
```

**Benefits:**

- Eliminates unnecessary indirection
- Makes code more explicit and readable
- Reduces complexity for simple cases

### 1. Extract Module

**Before:** Everything in one file

```python
# books.py (original)
# - Route handlers
# - Exception classes
# - Response formatting
# - Error handling
# All mixed together in 100+ lines
```

**After:** Separated concerns

```python
# books.py - Routes only
# api_response.py - Response formatting
# rescue.py - Exception handling
# exceptions/ - Exception classes
```

### 2. Replace Magic Numbers with Named Constants

**Before:**

```python
raise HTTPException(status_code=404, detail="Not found")  # Magic number
```

**After:**

```python
class RecordNotFound(APIException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(message, 404)  # Encapsulated in class
```

### 3. Consolidate Duplicate Conditional Fragments

**Before:** Scattered error handling

```python
# In multiple places:
if not found:
    return {"error": "Not found"}, 404
if invalid:
    return {"error": "Invalid"}, 422
```

**After:** Centralized error handling

```python
# Single place for all error formatting
@app.exception_handler(RecordNotFound)
async def handle_not_found(_request, exc):
    return json_response({"errors": {"message": exc.message}}, status=exc.status_code)
```

### 4. Replace Nested Conditional with Guard Clauses

**Before:**

```python
async def update(book_id: int, updates=Body()):
    for i, book in enumerate(BOOKS):
        if book.get("id") == book_id:
            # Nested logic here
            for key, value in updates.items():
                if key != "id":
                    book[key] = value
            return book
    # Error handling at end
```

**After:**

```python
async def update(book_id: int, updates=Body()):
    for i, book in enumerate(BOOKS):
        if book.get("id") == book_id:
            # Update logic
            return book
    raise RecordNotFound("Book", book_id)  # Guard clause - early return
```

## 🌐 API Design Patterns

### 0. Request/Response Validation Pattern

**Implementation:** Pydantic models as FastAPI parameters

FastAPI automatically handles validation and serialization:

```python
@app.post("/books", response_model=Book)
async def create(new_book: BookCreate):  # Validates input
    # FastAPI validates new_book against BookCreate schema
    # Returns data serialized against Book schema
    return book_data
```

**Benefits:**

- Automatic input validation with detailed error messages
- Consistent output serialization
- Self-generating OpenAPI documentation
- Type safety throughout the application

### 1. RESTful Resource Design

**Before:** Non-standard URLs

```
POST /books/create_book
PUT  /books/update_book
DELETE /books/delete_book/{id}
```

**After:** Standard REST conventions

```
POST   /books          # Create
GET    /books          # Index
GET    /books/{id}     # Show
PUT    /books/{id}     # Update (full)
PATCH  /books/{id}     # Update (partial)
DELETE /books/{id}     # Destroy
```

### 2. Consistent Error Response Format

All errors follow same structure:

```json
{
  "errors": {
    "message": "Book with identifier '123' not found"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. HTTP Status Code Standards

- `200` - Success
- `204` - No Content (DELETE operations)
- `400` - Bad Request (client error)
- `404` - Not Found
- `422` - Unprocessable Entity (validation errors)
- `500` - Internal Server Error

## 📁 Code Organization Patterns

### Module Pattern

Each file has a clear, single purpose:

```
Project 1/
├── api_response.py      # Response utilities
├── books.py             # Main application routes
├── rescue.py            # Exception handling
├── models/              # Pydantic models (DTOs)
│   ├── __init__.py
│   ├── book.py
│   ├── book_create.py
│   ├── book_update.py
│   └── error_response.py
└── exceptions/          # Exception definitions
    ├── __init__.py
    ├── api_exception.py
    ├── record_not_found.py
    ├── record_invalid.py
    └── ...
```

### Configuration Pattern

Centralized setup through configuration functions:

```python
# Main app just calls setup functions
app = FastAPI()
setup_exception_handlers(app)  # All configuration encapsulated
```

## 🎉 Benefits Achieved

1. **Maintainability** - Easy to find and modify specific functionality
2. **Testability** - Each component can be tested in isolation
3. **Extensibility** - Adding new features doesn't require changing existing code
4. **Consistency** - Uniform patterns across the entire codebase
5. **Readability** - Clear separation of concerns makes code self-documenting
6. **Reusability** - Components like `json_response` can be used anywhere
7. **Type Safety** - Pydantic models provide runtime validation and IDE support
8. **Self-Documenting** - API automatically generates accurate OpenAPI schemas

## 📚 References

- **Design Patterns:** Gang of Four (GoF) Design Patterns
- **Clean Code:** Robert C. Martin
- **Refactoring:** Martin Fowler
- **SOLID Principles:** Robert C. Martin
- **REST API Design:** Roy Fielding's dissertation on REST
