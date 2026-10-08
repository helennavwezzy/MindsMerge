from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from libs import jwt_auth

from .driver import driver
from .models import User, UserStats

security = HTTPBearer(auto_error=False)


def get_current_username(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """
    FastAPI dependency that extracts the current authenticated username from the JWT token.
    Returns only the username without querying the database.
    """
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    token = credentials.credentials
    try:
        return jwt_auth.validate_token(token)
    except ValueError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid authentication token"
        )


def get_current_user(
    username: str = Depends(get_current_username),
) -> User:
    """
    FastAPI dependency that extracts the current authenticated user from the JWT token.
    Returns the full User object from the database.
    """

    # Fetch user from database
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {name:$name})-[:HAS_STATS]->(s:UserStats)
            SET u.last_active = datetime()
            RETURN u, s
            """,
            name=username,
        )

        if (record := result.single()) is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "User not found",
            )

    user = User(**record["u"], stats=UserStats(**record["s"]))
    return user
