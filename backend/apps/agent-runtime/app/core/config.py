"""Application configuration module."""

from enum import StrEnum
from functools import lru_cache
from typing import Any, Self

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Execution environment classification."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


class LogLevel(StrEnum):
    """Controlled logging severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Strongly typed, validated application settings and environment boundaries."""

    # Application settings
    app_name: str = Field(default="AGENTPAY API", validation_alias="APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    app_env: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias=AliasChoices("APP_ENV", "app_env"),
    )

    debug: bool = Field(default=False, validation_alias="DEBUG")
    description: str = Field(
        default=(
            "Backend API platform for secure autonomous agentic commerce "
            "and payment infrastructure."
        ),
        validation_alias="DESCRIPTION",
    )

    # Server settings
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT", ge=1, le=65535)

    # API settings
    api_prefix: str = Field(default="/api", validation_alias="API_PREFIX")
    api_v1_prefix: str = Field(default="/v1", validation_alias="API_V1_PREFIX")

    # Documentation settings
    docs_enabled: bool = Field(default=True, validation_alias="DOCS_ENABLED")
    redoc_enabled: bool = Field(default=True, validation_alias="REDOC_ENABLED")
    openapi_enabled: bool = Field(default=True, validation_alias="OPENAPI_ENABLED")
    docs_url_path: str | None = Field(default="/docs", validation_alias="DOCS_URL")
    redoc_url_path: str | None = Field(default="/redoc", validation_alias="REDOC_URL")
    openapi_url_path: str | None = Field(default="/openapi.json", validation_alias="OPENAPI_URL")

    # Logging foundation settings
    log_level: LogLevel = Field(default=LogLevel.INFO, validation_alias="LOG_LEVEL")

    # Database foundation settings (Phase 013 Configuration Management)
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(
        default_factory=lambda: SecretStr("postgres_dev_pass"),
        validation_alias="POSTGRES_PASSWORD",
    )
    postgres_db: str = Field(default="agentpay_dev", validation_alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT", ge=1, le=65535)

    database_url: SecretStr | None = Field(default=None, validation_alias="DATABASE_URL")

    # Database Connection Pool & Timeout settings (Phase 013)
    db_pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE", ge=1, le=100)
    db_max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW", ge=0, le=100)
    db_pool_timeout: float = Field(
        default=30.0, validation_alias="DB_POOL_TIMEOUT", ge=0.1, le=300.0
    )
    db_pool_recycle: int = Field(default=1800, validation_alias="DB_POOL_RECYCLE", ge=1, le=86400)
    db_pool_pre_ping: bool = Field(default=True, validation_alias="DB_POOL_PRE_PING")
    db_connect_timeout: float = Field(
        default=10.0, validation_alias="DB_CONNECT_TIMEOUT", ge=0.1, le=60.0
    )

    # Database Backup & Retention Settings (P2-01)
    backup_retention_days: int = Field(default=30, validation_alias="BACKUP_RETENTION_DAYS")
    wal_retention_hours: int = Field(default=72, validation_alias="WAL_RETENTION_HOURS")
    s3_backup_bucket: str | None = Field(default=None, validation_alias="S3_BACKUP_BUCKET")
    s3_backup_endpoint: str | None = Field(default=None, validation_alias="S3_BACKUP_ENDPOINT")
    db_command_timeout: float = Field(
        default=30.0, validation_alias="DB_COMMAND_TIMEOUT", ge=0.1, le=300.0
    )

    # Redis foundation settings (Protected SecretStr)
    redis_url: SecretStr | None = Field(default=None, validation_alias="REDIS_URL")

    # Security & Cryptographic secret foundation settings (Protected SecretStr)
    secret_key: SecretStr | None = Field(default=None, validation_alias="SECRET_KEY")
    jwt_secret: SecretStr = Field(
        default_factory=lambda: SecretStr("dev_jwt_secret_change_in_production_32chars_min"),
        validation_alias="JWT_SECRET",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=15, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", ge=1, le=1440
    )
    refresh_token_expire_days: int = Field(
        default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS", ge=1, le=365
    )
    jwt_issuer: str = Field(default="agentpay-api", validation_alias="JWT_ISSUER")
    jwt_audience: str = Field(default="agentpay-client", validation_alias="JWT_AUDIENCE")
    api_key: SecretStr | None = Field(default=None, validation_alias="API_KEY")
    client_secret: SecretStr | None = Field(default=None, validation_alias="CLIENT_SECRET")

    # Payment Provider Settings — Razorpay Foundation (Phase 286)
    razorpay_key_id: str | None = Field(default=None, validation_alias="RAZORPAY_KEY_ID")
    razorpay_key_secret: SecretStr | None = Field(
        default=None, validation_alias="RAZORPAY_KEY_SECRET"
    )
    razorpay_webhook_secret: SecretStr | None = Field(
        default=None, validation_alias="RAZORPAY_WEBHOOK_SECRET"
    )
    razorpay_enabled: bool = Field(default=False, validation_alias="RAZORPAY_ENABLED")

    # Security foundation settings

    cors_allowed_origins: list[str] | str = Field(
        default_factory=lambda: ["http://localhost:3000"],
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS", "cors_allowed_origins"),
    )
    cors_allow_credentials: bool = Field(
        default=False,
        validation_alias=AliasChoices("CORS_ALLOW_CREDENTIALS", "cors_allow_credentials"),
    )

    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["*"], validation_alias="ALLOWED_HOSTS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def validate_cors_allowed_origins(cls, v: Any) -> list[str]:
        """Normalize comma-separated CORS origins and validate origin format."""
        if isinstance(v, str):
            origins = [o.strip() for o in v.split(",") if o.strip()]
        elif isinstance(v, (list, tuple, set)):
            origins = [str(o).strip() for o in v if str(o).strip()]
        else:
            return ["http://localhost:3000"]

        normalized: list[str] = []
        for origin in origins:
            if origin == "*":
                normalized.append("*")
                continue
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid CORS origin format '{origin}'.")
            clean_origin = origin.rstrip("/")
            normalized.append(clean_origin)

        return normalized

    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, v: SecretStr | str | None) -> SecretStr | None:
        """Validate secret_key length and non-emptiness without revealing value in traceback."""
        if v is None:
            return None
        raw_val = v.get_secret_value() if isinstance(v, SecretStr) else str(v)
        if not raw_val or not raw_val.strip():
            raise ValueError("SECRET_KEY cannot be empty.")
        if len(raw_val) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return SecretStr(raw_val) if isinstance(v, str) else v

    @model_validator(mode="after")
    def validate_production_and_pool_safety(self) -> Self:
        """Enforce production security rules and pool safety checks."""
        # 1. Phase 015 Pool Parameter Validations
        if self.db_pool_size <= 0:
            raise ValueError("db_pool_size must be greater than 0.")
        if self.db_max_overflow < 0:
            raise ValueError("db_max_overflow must be greater than or equal to 0.")
        if self.db_pool_timeout <= 0:
            raise ValueError("db_pool_timeout must be greater than 0.")
        if self.db_pool_recycle < 0:
            raise ValueError("db_pool_recycle must be greater than or equal to 0.")

        # 2. Production Safety Guards
        if self.app_env == Environment.PRODUCTION:
            if self.debug:
                raise ValueError("DEBUG mode cannot be enabled in PRODUCTION environment.")

            if "*" in self.cors_allowed_origins:
                raise ValueError("Wildcard origin '*' is prohibited in PRODUCTION environment.")

            unsafe_passwords = {"postgres_dev_pass", "postgres", "admin", "password", "root"}
            pwd = self.postgres_password.get_secret_value().lower()
            if pwd in unsafe_passwords:
                raise ValueError(
                    f"Default development password '{self.postgres_password.get_secret_value()}' "
                    "is prohibited in PRODUCTION environment."
                )

            if self.postgres_host.lower() in {"localhost", "127.0.0.1"} and not self.database_url:
                raise ValueError(
                    "Localhost database host 'localhost' is prohibited in PRODUCTION environment."
                )

            jwt_sec = self.jwt_secret.get_secret_value()
            if not jwt_sec or len(jwt_sec) < 32 or "dev_jwt_secret" in jwt_sec:
                raise ValueError(
                    "Default or weak JWT_SECRET is prohibited in PRODUCTION environment."
                )

        # 3. Test Environment Safety Guard
        if self.app_env == Environment.TEST:
            target_url = self.effective_database_url.get_secret_value().lower()
            unsafe_kw = ["prod", "production", "staging", "rds.amazonaws.com", "database.azure.com"]
            for keyword in unsafe_kw:
                if keyword in target_url:
                    msg = f"Test environment cannot target PROD/STAGING database ('{keyword}')."
                    raise ValueError(msg)

        # 4. CORS Credentials Guard
        if "*" in self.cors_allowed_origins and self.cors_allow_credentials:
            raise ValueError("Wildcard origin '*' cannot be combined with allow_credentials=True.")

        return self

    # Backward compatibility properties for Phase 011 / 012 integration points
    @property
    def title(self) -> str:
        """Alias for app_name."""
        return self.app_name

    @property
    def version(self) -> str:
        """Alias for app_version."""
        return self.app_version

    @property
    def api_v1_str(self) -> str:
        """Construct full v1 API string prefix."""
        return f"{self.api_prefix}{self.api_v1_prefix}"

    @property
    def docs_url(self) -> str | None:
        """Return docs URL path if enabled."""
        return self.docs_url_path if self.docs_enabled else None

    @property
    def redoc_url(self) -> str | None:
        """Return ReDoc URL path if enabled."""
        return self.redoc_url_path if self.redoc_enabled else None

    @property
    def openapi_url(self) -> str | None:
        """Return OpenAPI JSON schema URL path if enabled."""
        return self.openapi_url_path if self.openapi_enabled else None

    # Environment convenience properties for Phase 014
    @property
    def environment(self) -> Environment:
        """Return the current execution environment."""
        return self.app_env

    @property
    def is_local(self) -> bool:
        """Check if execution environment is local."""
        return self.app_env == Environment.LOCAL

    @property
    def is_development(self) -> bool:
        """Check if execution environment is development."""
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_test(self) -> bool:
        """Check if execution environment is test."""
        return self.app_env == Environment.TEST

    @property
    def is_staging(self) -> bool:
        """Check if execution environment is staging."""
        return self.app_env == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if execution environment is production."""
        return self.app_env == Environment.PRODUCTION

    @property
    def effective_database_url(self) -> SecretStr:
        """Return canonical SQLAlchemy asyncpg connection URL."""

        if self.database_url and self.database_url.get_secret_value().strip():
            raw_url = self.database_url.get_secret_value().strip()
            if raw_url.startswith("postgresql://"):
                normalized = "postgresql+asyncpg://" + raw_url[len("postgresql://") :]
            elif raw_url.startswith("postgres://"):
                normalized = "postgresql+asyncpg://" + raw_url[len("postgres://") :]
            elif not raw_url.startswith("postgresql+asyncpg://"):
                normalized = f"postgresql+asyncpg://{raw_url}"
            else:
                normalized = raw_url
            return SecretStr(normalized)

        pwd = self.postgres_password.get_secret_value()
        url = (
            f"postgresql+asyncpg://{self.postgres_user}:{pwd}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return SecretStr(url)

    # Safe diagnostic summary API for Phase 013 & Phase 015
    @property
    def safe_summary(self) -> dict[str, Any]:
        """Return non-sensitive configuration dictionary for diagnostic logging."""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "app_env": self.app_env.value,
            "debug": self.debug,
            "host": self.host,
            "port": self.port,
            "api_prefix": self.api_prefix,
            "api_v1_prefix": self.api_v1_prefix,
            "docs_enabled": self.docs_enabled,
            "redoc_enabled": self.redoc_enabled,
            "openapi_enabled": self.openapi_enabled,
            "log_level": self.log_level.value,
            "postgres_user": self.postgres_user,
            "postgres_host": self.postgres_host,
            "postgres_port": self.postgres_port,
            "postgres_db": self.postgres_db,
            "db_pool_size": self.db_pool_size,
            "db_max_overflow": self.db_max_overflow,
            "db_pool_timeout": self.db_pool_timeout,
            "db_pool_recycle": self.db_pool_recycle,
            "db_pool_pre_ping": self.db_pool_pre_ping,
            "db_connect_timeout": self.db_connect_timeout,
            "db_command_timeout": self.db_command_timeout,
            "postgres_password": "[REDACTED]" if self.postgres_password else None,
            "secret_key": "[REDACTED]" if self.secret_key else None,
            "database_url": "[REDACTED]" if self.database_url else None,
            "effective_database_url": "[REDACTED]",
            "redis_url": "[REDACTED]" if self.redis_url else None,
            "jwt_secret": "[REDACTED]" if self.jwt_secret else None,
            "api_key": "[REDACTED]" if self.api_key else None,
            "client_secret": "[REDACTED]" if self.client_secret else None,
            "razorpay_key_id": self.razorpay_key_id,
            "razorpay_key_secret": "[REDACTED]" if self.razorpay_key_secret else None,
            "razorpay_webhook_secret": "[REDACTED]" if self.razorpay_webhook_secret else None,
            "razorpay_enabled": self.razorpay_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    """Cached settings provider producing an immutable Settings singleton instance."""
    return Settings()


# Default settings instance for convenience
settings: Settings = get_settings()
