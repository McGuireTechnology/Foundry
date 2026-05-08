from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Foundry API"
    env: str = "dev"
    api_current_version: str = "v1"
    api_version_header_name: str = "X-API-Version"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/foundry"

    # TODO: Replace defaults with secure env-managed values before production.
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 14
    reset_password_token_expire_minutes: int = 30
    login_max_attempts: int = 5
    login_lockout_minutes: int = 15
    cors_allow_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias=AliasChoices("CORS_ALLOW_ORIGINS", "BACKEND_CORS_ORIGINS"),
    )
    cors_allow_origin_regex: str = Field(
        default=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        validation_alias=AliasChoices("CORS_ALLOW_ORIGIN_REGEX", "BACKEND_CORS_ORIGIN_REGEX"),
    )

    @property
    def cors_allow_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins_raw.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
