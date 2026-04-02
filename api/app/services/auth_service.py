import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from redis.asyncio import Redis

from app.config import settings

ALGORITHM = "HS256"


class AuthService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        return jwt.encode(
            {"sub": subject, "exp": expire, "type": "access"},
            settings.jwt_secret_key,
            algorithm=ALGORITHM,
        )

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
        return jwt.encode(
            {"sub": subject, "exp": expire, "type": "refresh", "jti": str(uuid.uuid4())},
            settings.jwt_secret_key,
            algorithm=ALGORITHM,
        )

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])

    async def is_token_revoked(self, jti: str) -> bool:
        return await self._redis.exists(f"revoked:{jti}") > 0

    async def revoke_token(self, jti: str, expires_in: int) -> None:
        await self._redis.setex(f"revoked:{jti}", expires_in, "1")

    def authenticate(self, email: str, password: str) -> bool:
        if email != settings.admin_email:
            return False
        if not settings.admin_password_hash:
            return False
        return self.verify_password(password, settings.admin_password_hash)
