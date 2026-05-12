"""FastAPI application factory."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import get_settings
from .database import create_db_and_tables
from .middleware.error_handler import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from .routers.router import api_v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create database tables on startup (idempotent)."""
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Passive Real Estate Underwriting & Evaluation Platform — REST API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── exception handlers ────────────────────────────────────────────────
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── routers ───────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    # ── health endpoint ───────────────────────────────────────────────────
    @app.get("/health", tags=["system"])
    async def health() -> dict:
        """Liveness probe — returns 200 when the server is running."""
        return {
            "success": True,
            "data": {
                "status": "ok",
                "environment": settings.environment,
                "version": "1.0.0",
            },
            "error": None,
        }

    return app


app = create_app()
