from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

import envy

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def create_access_token(username: str) -> str:
    """Create a JWT access token for a user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, envy.JWT_SECRET_KEY, algorithm=envy.JWT_ALGORITHM
    )
    return encoded_jwt


def validate_token(token: str) -> str:
    """
    Validate a JWT token and return the username.
    Raises `ValueError` if token is invalid.
    """
    try:
        payload = jwt.decode(
            token, envy.JWT_SECRET_KEY, algorithms=[envy.JWT_ALGORITHM]
        )
    except JWTError:
        raise ValueError("Invalid authentication token.")

    username = payload.get("sub")
    if username is None or not isinstance(username, str):
        raise ValueError("Invalid authentication credentials")

    return username


def validate_auth_header(auth_header: str) -> str:
    """
    Validate the Authorization header and return the username.
    Raises `ValueError` if header or header's token is invalid.
    """
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise ValueError("Invalid Authorization header format.")

    return validate_token(token)
