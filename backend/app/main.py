from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine

# Import models so SQLAlchemy knows about them before create_all runs
import app.models.submission  # noqa: F401

from app.routers import submissions
from app.routers import admin
# Create all database tables on startup (safe to run multiple times)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register the submissions router — all its routes become part of the app
app.include_router(submissions.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    """Quick check that the server is running."""
    return {"status": "ok", "app": settings.app_name}
