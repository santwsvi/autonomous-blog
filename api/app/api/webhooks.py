import hashlib
import hmac

import structlog
from fastapi import APIRouter, Header, HTTPException, Request, status

from app.config import settings

logger = structlog.get_logger()
router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/revalidate", status_code=status.HTTP_200_OK)
async def revalidate_isr(
    request: Request,
    x_revalidation_signature: str | None = Header(None),
) -> dict:
    if not x_revalidation_signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature")

    body = await request.body()
    expected = hmac.new(
        settings.revalidation_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(x_revalidation_signature, expected):
        logger.warning("webhook_invalid_signature")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    logger.info("webhook_revalidation_triggered")
    # In production, this would call Vercel's revalidation API
    return {"revalidated": True}
