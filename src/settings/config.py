import json
import os
import secrets

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    VERSION: str = "0.1.0"
    APP_TITLE: str = os.getenv("APP_TITLE", "Vue FastAPI Admin")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Vue FastAPI Admin")
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
    )

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ]
    CORS_ALLOW_HEADERS: list = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ]

    DEBUG: bool = True
    APP_ENV: str = "development"

    PROJECT_ROOT: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4  # 4 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days for refresh token
    # Database configuration
    DB_ENGINE: str = "postgres"  # Default to PostgreSQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = "fastapi_backend"

    @property
    def TORTOISE_ORM(self) -> dict:
        """Dynamically generate Tortoise ORM configuration"""
        if self.DB_ENGINE == "postgres":
            return {
                "connections": {
                    "default": {
                        "engine": "tortoise.backends.asyncpg",
                        "credentials": {
                            "host": self.DB_HOST,
                            "port": self.DB_PORT,
                            "user": self.DB_USER,
                            "password": self.DB_PASSWORD,
                            "database": self.DB_NAME,
                            # Connection pool configuration
                            "minsize": 1,
                            "maxsize": 20,
                            "max_queries": 50000,
                            "max_inactive_connection_lifetime": 300,
                            "timeout": 60,
                            "command_timeout": 60,
                        },
                    }
                },
                "apps": {
                    "models": {
                        "models": ["models", "aerich.models"],
                        "default_connection": "default",
                    },
                },
                "use_tz": False,
                "timezone": "Asia/Shanghai",
            }
        else:
            # SQLite fallback configuration
            return {
                "connections": {
                    "default": {
                        "engine": "tortoise.backends.sqlite",
                        "credentials": {"file_path": f"{self.BASE_DIR}/db.sqlite3"},
                    }
                },
                "apps": {
                    "models": {
                        "models": ["models", "aerich.models"],
                        "default_connection": "default",
                    },
                },
                "use_tz": False,
                "timezone": "Asia/Shanghai",
            }

    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Swagger
    SWAGGER_UI_USERNAME: str = os.getenv("SWAGGER_UI_USERNAME", "admin")
    SWAGGER_UI_PASSWORD: str = os.getenv("SWAGGER_UI_PASSWORD", "")
    COMPANY_ROLE_MAPPING: dict[str, list[int]] = {"default": []}

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = 300  # Default cache expiration time (seconds)

    @field_validator("COMPANY_ROLE_MAPPING", mode="before")
    @classmethod
    def parse_company_role_mapping(cls, v):
        """Parse COMPANY_ROLE_MAPPING environment variable"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"default": []}
        return v

    @field_validator("DB_PASSWORD")
    @classmethod
    def validate_db_password(cls, v):
        """Validate database password"""
        app_env = os.getenv("APP_ENV", "development")
        # Testing and development environments allow empty password
        if not v and app_env == "production":
            raise ValueError("Database password must be set in production environment")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY strength"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("SWAGGER_UI_PASSWORD")
    @classmethod
    def validate_swagger_password(cls, v):
        """Validate Swagger access password"""
        import os

        # Testing environment allows empty password
        if os.getenv("APP_ENV") == "testing":
            return v or "test_password"
        if not v:
            raise ValueError("SWAGGER_UI_PASSWORD must be set")
        if len(v) < 8:
            raise ValueError("Swagger access password must be at least 8 characters long")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Additional environment-specific validation
        if self.APP_ENV == "production":
            self._validate_production_config()

    def _validate_production_config(self):
        """Production environment specific configuration validation"""
        if self.DEBUG:
            raise ValueError("DEBUG mode cannot be enabled in production environment")

        if self.DB_ENGINE == "sqlite":
            raise ValueError("Production environment should use PostgreSQL instead of SQLite")

        if "localhost" in self.CORS_ORIGINS:
            raise ValueError("Production environment should not allow localhost CORS access")


settings = Settings()
