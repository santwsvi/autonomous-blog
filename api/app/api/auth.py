import time

import structlog
from fastapi import APIRouter, HTTPException, status

from app.api.deps import AuthSvc
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, auth_service: AuthSvc) -> TokenResponse:
    if not auth_service.authenticate(body.email, body.password):
        logger.warning("login_failed", email=body.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    logger.info("login_success", email=body.email)
    return TokenResponse(
        access_token=auth_service.create_access_token(body.email),
        refresh_token=auth_service.create_refresh_token(body.email),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, auth_service: AuthSvc) -> TokenResponse:
    try:
        payload = auth_service.decode_token(body.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti", "")
    if await auth_service.is_token_revoked(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    # Revoke the used refresh token (rotation)
    exp = payload.get("exp", 0)
    ttl = max(exp - int(time.time()), 1)
    await auth_service.revoke_token(jti, ttl)

    subject = payload["sub"]
    logger.info("token_refreshed", subject=subject)
    return TokenResponse(
        access_token=auth_service.create_access_token(subject),
        refresh_token=auth_service.create_refresh_token(subject),
    )
