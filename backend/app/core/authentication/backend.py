from fastapi_users.authentication import AuthenticationBackend

from .strategy import get_jwt_strategy
from .transport import bearer_transport, cookie_transport

auth_bearer_backend = AuthenticationBackend(
    name="auth-bearer-jwt-backend",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
auth_cookie_backend = AuthenticationBackend(
    name="auth-cookie-jwt-backend",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
