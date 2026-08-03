import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.logging import get_logger

security_logger = get_logger("app.security")

# Every deployment MUST override this via the JWT_SECRET_KEY environment variable - see
# Documentation/DEPLOYMENT.md. The fallback below is only safe for local development; two sites
# sharing the same secret could forge each other's access tokens.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid4())

    if "iat" not in to_encode:
        to_encode["iat"] = int(datetime.now(timezone.utc).timestamp())

    to_encode.update({"exp": int(expire.timestamp())})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):
    """Returns the decoded payload, or None on ANY failure - this return-type contract is
    unchanged so every existing call site (get_current_user, get_current_user_and_session, ...)
    keeps working exactly as before. What's new is that this single chokepoint - every JWT
    decode in the app passes through here - now distinguishes and logs *why* a token was
    rejected as a security event (Module: centralized security logging), never logging the
    token itself (see app.core.json_logging's redaction, which also independently strips any
    field literally named token/jwt/authorization as a second layer of defense)."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except ExpiredSignatureError:
        security_logger.warning(
            "JWT rejected: expired", extra={"action": "JWT_EXPIRED", "success": False},
        )
        return None
    except JWTError:
        security_logger.warning(
            "JWT rejected: invalid", extra={"action": "JWT_INVALID", "success": False},
        )
        return None
