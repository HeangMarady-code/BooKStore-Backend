import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401  (ensure all models are registered)

logger = logging.getLogger("uvicorn.error")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS - allow all origins for development
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create database tables on startup (don't crash if DB is unreachable yet)
    @application.on_event("startup")
    def on_startup() -> None:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ensured. Connection OK.")
        except Exception as exc:  # noqa: BLE001 - startup should not crash
            logger.warning(
                "Database is not reachable yet. API will start anyway. "
                "Fix DATABASE_CONNECTION_URL/.env to enable DB features. Error: %s",
                exc,
            )

    application.include_router(api_router, prefix="/api/v1")

    @application.get("/")
    def root():
        return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}

    @application.get("/health")
    def health_check():
        return {"status": "ok"}

    return application


app = create_application()