import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.auth import router as auth_router
from app.api.v1.generate import router as generate_router
from app.api.v1.posts import router as posts_router
from app.api.webhooks import router as webhooks_router
from app.config import settings
from app.middleware.security_headers import SecurityHeadersMiddleware

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", app_name=settings.app_name)
    yield
    logger.info("app_shutting_down")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
)

app.state.limiter = limiter

# Middleware (order matters — last added = first executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = str(uuid.uuid4())
    logger.error(
        "unhandled_exception",
        request_id=request_id,
        method=request.method,
        path=str(request.url.path),
        error=str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "request_id": request_id},
    )


# Routes
app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(generate_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/openapi.json", include_in_schema=False)
async def openapi_spec() -> dict:
    return app.openapi()
