"""FastAPI TodoApp main application entry point."""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from config import settings
from routers import auth, todos, admin, users


app = FastAPI()

# Tables are managed by Alembic migrations
# settings.base.metadata.create_all(bind=settings.database_engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
