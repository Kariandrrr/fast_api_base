from fastapi_users.authentication import CookieTransport, BearerTransport

from app.core.config.main_config import settings

cookie_transport = CookieTransport(
    cookie_name=settings.auth.cookie.access_name,
    cookie_max_age=settings.auth.cookie.max_age,
    cookie_path=settings.auth.cookie.path,
    cookie_domain=settings.auth.cookie.domain,
    cookie_secure=settings.auth.cookie.secure,
    cookie_httponly=settings.auth.cookie.httponly,
    cookie_samesite=settings.auth.cookie.samesite,
)

bearer_transport = BearerTransport(tokenUrl=settings.api.bearer_token_url)
