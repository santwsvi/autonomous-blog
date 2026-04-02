from typing import Annotated

import jwt
import structlog
from fastapi import Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.repositories.post_repository import PostRepository
from app.services.auth_service import AuthService

logger = structlog.get_logger()

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def get_auth_service(redis: Redis = Depends(get_redis)) -> AuthService:
    return AuthService(redis)


async def get_post_repository(db: AsyncSession = Depends(get_db)) -> PostRepository:
    return PostRepository(db)


async def require_auth(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload["sub"]
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


# Type aliases for dependency injection
Db = Annotated[AsyncSession, Depends(get_db)]
Auth = Annotated[str, Depends(require_auth)]
PostRepo = Annotated[PostRepository, Depends(get_post_repository)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
RedisClient = Annotated[Redis, Depends(get_redis)]
