import os

from pydantic import BaseModel, PostgresDsn, RedisDsn


class DatabasePostgresqlConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    ca_path: str = os.path.normpath(os.path.join(os.getcwd(), "certs", "ca.pem"))
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class DatabaseRedisConfig(BaseModel):
    url: RedisDsn


class DatabaseConfig(BaseModel):
    pg: DatabasePostgresqlConfig
    redis: DatabaseRedisConfig
