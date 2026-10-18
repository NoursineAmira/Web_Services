from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, request

from config import JWT_SECRET
from validation import ApiError

ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=5)


def create_token(username, role):
    now = datetime.now(timezone.utc)
    claims = {"sub": username, "role": role, "iat": now, "exp": now + TOKEN_TTL}
    return jwt.encode(claims, JWT_SECRET, algorithm=ALGORITHM)


def require_role(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            scheme, _, token = request.headers.get("Authorization", "").partition(" ")
            if scheme.lower() != "bearer" or not token.strip():
                raise ApiError(401, "AUTH_REQUIRED", "Missing or malformed Authorization header, expected 'Bearer <token>'")
            try:
                claims = jwt.decode(
                    token.strip(), JWT_SECRET, algorithms=[ALGORITHM], options={"require": ["sub", "role", "exp"]}
                )
            except jwt.ExpiredSignatureError:
                raise ApiError(401, "TOKEN_EXPIRED", "Token has expired, log in again") from None
            except jwt.InvalidTokenError:
                raise ApiError(401, "INVALID_TOKEN", "Token is invalid") from None
            if claims["role"] not in roles:
                raise ApiError(403, "FORBIDDEN", f"Role '{claims['role']}' is not allowed to access this resource")
            g.user = claims
            return view(*args, **kwargs)

        return wrapper

    return decorator
