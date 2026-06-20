from pydantic_settings import BaseSettings, SettingsConfigDict

from .api_auth_config import AuthConfig
from .api_config import APIConfig
from .cors_config import CORSConfig
from .database_config import DatabaseConfig
from .invitations_config import InvitationsConfig
from .run_config import RunConfig
from .uploads_config import UploadsConfig


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=("env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: APIConfig = APIConfig()
    db: DatabaseConfig
    auth: AuthConfig
    uploads: UploadsConfig = UploadsConfig()
    invitations: InvitationsConfig = InvitationsConfig()
    cors: CORSConfig

    @property
    def sync_database_url(self) -> str:
        return str(
            self.db.pg.url
            ).replace(
            "postgresql+asyncpg://",
            "postgresql+psycopg2://"
        )


settings = Settings()
