from fastapi import APIRouter, Depends, HTTPException, status

from ..depends import get_current_user
from ..driver import driver
from ..models import User
from ..schemas import ResponseModel, UserPatchRequest

router = APIRouter(prefix="/users")


@router.get("/me")
def whoami(user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return user


@router.get("/{username}")
def get_user(username: str):
    """Get user profile with statistics."""

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {name:$name})-[:HAS_STATS]->(s:UserStats)
            RETURN u, s
            """,
            name=username,
        )

        if (record := result.single()) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return User(**record["u"], stats=record["s"])


@router.patch("/me")
def patch_user(body: UserPatchRequest, user: User = Depends(get_current_user)):
    """Update current user's profile (bio and/or avatar_url)."""

    user.bio = body.bio if body.bio is not None else user.bio
    user.avatar_url = (
        None
        if body.remove_avatar
        else (body.avatar_url if body.avatar_url is not None else user.avatar_url)
    )

    with driver.session() as session:
        session.run(
            """
            MATCH (u:User {name:$name})
            SET u.bio=$bio, u.avatar_url=$avatar_url
            """,
            name=user.name,
            bio=user.bio,
            avatar_url=user.avatar_url,
        )

    return ResponseModel(
        result=user.dump(),
        message="user profile updated successfully",
    )
