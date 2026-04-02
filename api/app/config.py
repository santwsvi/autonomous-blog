from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Database
    database_url: str = "postgresql+asyncpg://blog:blog@localhost:5432/blog"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Auth
    jwt_secret_key: str = "change-me-in-production-min-32-chars"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    admin_email: str = "admin@blog.com"
    admin_password_hash: str = ""  # bcrypt hash

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Webhook
    revalidation_secret: str = "change-me-min-32-chars"

    # LLM
    openai_api_key: str = ""
    llm_ssl_verify: bool = True

    # Observability
    sentry_dsn: str = ""

    # App
    app_name: str = "Autonomous Blog API"
    log_level: str = "INFO"
    debug: bool = False


settings = Settings()
