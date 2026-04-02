"""Tests for auth service."""

import pytest

from app.services.auth_service import AuthService


class FakeRedis:
    """Minimal fake Redis for testing."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = value


@pytest.fixture
def auth_service():
    return AuthService(redis=FakeRedis())


class TestAuthService:
    def test_create_access_token(self, auth_service):
        token = auth_service.create_access_token("test@blog.com")
        payload = auth_service.decode_token(token)
        assert payload["sub"] == "test@blog.com"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_refresh_token(self, auth_service):
        token = auth_service.create_refresh_token("test@blog.com")
        payload = auth_service.decode_token(token)
        assert payload["sub"] == "test@blog.com"
        assert payload["type"] == "refresh"
        assert "jti" in payload

    def test_access_token_different_from_refresh(self, auth_service):
        access = auth_service.create_access_token("test@blog.com")
        refresh = auth_service.create_refresh_token("test@blog.com")
        assert access != refresh

    @pytest.mark.asyncio
    async def test_revoke_and_check(self, auth_service):
        assert not await auth_service.is_token_revoked("test-jti")
        await auth_service.revoke_token("test-jti", 3600)
        assert await auth_service.is_token_revoked("test-jti")

    def test_verify_password(self, auth_service):
        import bcrypt

        hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
        assert auth_service.verify_password("secret", hashed) is True
        assert auth_service.verify_password("wrong", hashed) is False
