
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes.customer import router as customer_router
from app.core.config import get_settings
from app.core.database import init_db
from app.utils.exceptions import register_exception_handlers
from app.utils.logging import setup_logging

BASE_DIR = Path(__file__).resolve().parent.parent

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    logger.info("Database ready")
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Loan lending customer management — create and retrieve customer records.",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(customer_router)


@app.get("/health", tags=["Health"])
def health_check() -> JSONResponse:
    return JSONResponse(
        content={
            "success": True,
            "message": "Service is healthy",
            "version": settings.APP_VERSION,
        }
    )


@app.get("/", include_in_schema=False)
def serve_dashboard() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
