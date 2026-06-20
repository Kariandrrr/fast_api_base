from pathlib import Path
from typing import Literal

from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent.parent.parent

EXPIRE_SECONDS: int = 900


class AuthJWTConfig(BaseModel):
    # Секреты
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    # access
    access_token_lifetime_seconds: int = EXPIRE_SECONDS
    access_token_audience: str = "worktrack:access"
    # refresh
    refresh_token_lifetime_seconds: int = 60 * 60 * 24 * 30
    refresh_token_audience: str = "worktrack:refresh"
    # Сброс пароля
    reset_password_token_secret: str
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = "worktrack:reset"
    # Подтверждение email
    verification_token_secret: str
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = "worktrack:verify"


class AuthCookieConfig(BaseModel):
    access_name: str = "access_token"
    refresh_name: str = "refresh_token"
    max_age: int = EXPIRE_SECONDS
    path: str = "/"
    refresh_path: str = "/api/auth/cookie"
    domain: str | None = None  # TODO: Поменять на проде
    secure: bool = False  # TODO: Поменять на проде
    httponly: bool = True
    samesite: Literal["lax", "strict", "none"] = "lax"


class AuthConfig(BaseModel):
    requires_verification: bool = False
    jwt: AuthJWTConfig
    cookie: AuthCookieConfig = AuthCookieConfig()
