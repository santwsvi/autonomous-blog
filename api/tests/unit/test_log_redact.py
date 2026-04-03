"""Tests for log redaction processor."""

from app.middleware.log_redact import redact_sensitive


class TestRedactSensitive:
    def test_redacts_bearer_token(self):
        event = {"event": "request", "auth": "Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"}
        result = redact_sensitive(None, None, event)
        assert "eyJ" not in result["auth"]
        assert "Bearer [REDACTED]" in result["auth"]

    def test_redacts_openai_key(self):
        event = {"event": "llm_call", "key": "sk-proj-abc123def456"}
        result = redact_sensitive(None, None, event)
        assert "abc123" not in result["key"]
        assert "sk-[REDACTED]" in result["key"]

    def test_redacts_password_key(self):
        event = {"password": "my-secret-password"}
        result = redact_sensitive(None, None, event)
        assert result["password"] == "[REDACTED]"

    def test_redacts_token_key(self):
        event = {"token": "some-jwt-token-value"}
        result = redact_sensitive(None, None, event)
        assert result["token"] == "[REDACTED]"

    def test_redacts_api_key_key(self):
        event = {"api_key": "sk-proj-abc123"}
        result = redact_sensitive(None, None, event)
        assert result["api_key"] == "[REDACTED]"

    def test_redacts_bcrypt_hash(self):
        event = {"event": "user", "hash": "$2b$12$UIJjAnQHhy/SrTUpaW/.AODcCFgZW"}
        result = redact_sensitive(None, None, event)
        assert "UIJjAnQHhy" not in result["hash"]

    def test_preserves_normal_values(self):
        event = {"event": "request", "path": "/api/v1/posts", "method": "GET", "status": 200}
        result = redact_sensitive(None, None, event)
        assert result["path"] == "/api/v1/posts"
        assert result["method"] == "GET"
        assert result["status"] == 200

    def test_preserves_non_string_values(self):
        event = {"count": 42, "active": True, "items": [1, 2, 3]}
        result = redact_sensitive(None, None, event)
        assert result["count"] == 42
        assert result["active"] is True
        assert result["items"] == [1, 2, 3]

    def test_case_insensitive_key_match(self):
        event = {"Authorization": "Bearer token123", "PASSWORD": "secret"}
        result = redact_sensitive(None, None, event)
        assert result["Authorization"] == "[REDACTED]"
        assert result["PASSWORD"] == "[REDACTED]"

    def test_password_in_value_string(self):
        event = {"event": "config", "detail": "password='secret123' loaded"}
        result = redact_sensitive(None, None, event)
        assert "secret123" not in result["detail"]
