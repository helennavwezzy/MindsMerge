import uuid
from ctypes import ArgumentError
from datetime import datetime, timezone
from typing import Literal

import neo4j.time
from pydantic import BaseModel, EmailStr, Field, field_validator

__all__ = ["User", "Post", "Comment"]


# helper funcs
def uuid4_hex():
    return uuid.uuid4().hex[:12]


def utcnow():
    return datetime.now(timezone.utc)


def to_datetime(v) -> datetime:
    if isinstance(v, neo4j.time.DateTime):
        return v.to_native()
    if isinstance(v, str):
        # e.g. "2025-11-16T07:55:12.123Z"
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    if isinstance(v, datetime):
        return v
    raise ArgumentError(f"Invalid parameter: {v}")


class UserStats(BaseModel):
    posts: int = 0
    comments: int = 0
    karma: int = 0


class User(BaseModel):
    name: str
    email: EmailStr | None = None
    """Email is missing for agent users."""

    password_hash: str | None = Field(default=None, exclude=True)

    avatar_url: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    last_active: datetime = Field(default_factory=utcnow)

    bio: str = ""
    """For an agent, `bio` refers to the agent's summary."""

    instruction: str | None = None
    """Instruction for the agent. None if user is not an agent."""

    stats: UserStats | None = None
    """Statistics of a user on the forum."""

    kind: Literal["agent", "human"] = "human"

    @field_validator("created_at", "last_active", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> datetime:
        return to_datetime(v)

    def dump(self, *, with_stats=False, exclude: set[str] | None = None):
        """Model dump with minimal data."""
        exclude = exclude or set()
        if with_stats and self.stats is not None:
            return self.model_dump(mode="json", exclude=exclude)
        return self.model_dump(mode="json", exclude={"stats", *exclude})


class TopicStats(BaseModel):
    pass


class Topic(BaseModel):
    name: str
    description: str
    stats: TopicStats = TopicStats()


class PostStats(BaseModel):
    upvotes: int = 0
    downvotes: int = 0
    num_comments: int = 0


class Post(BaseModel):
    id: str = Field(default_factory=uuid4_hex)
    title: str
    content: str

    topic: Topic | None = None
    created_at: datetime = Field(default_factory=utcnow)

    author: User
    """The author who composed this post."""

    stats: PostStats | None = None
    """Statistics of the post on the forum."""

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> datetime:
        return to_datetime(v)

    def dump(
        self, *, with_stats=False, with_author=False, exclude: set[str] | None = None
    ):
        """Model dump with minimal data."""
        exclude = {"stats", "author", *(exclude or set())}
        res = self.model_dump(mode="json", exclude=exclude)
        if with_author:
            res["author"] = self.author.dump()
        if with_stats and self.stats is not None:
            res["stats"] = self.stats.model_dump(mode="json")
        return res


class CommentStats(BaseModel):
    upvotes: int = 0
    downvotes: int = 0
    num_replies: int = 0


class Comment(BaseModel):
    id: str = Field(default_factory=uuid4_hex)
    content: str
    created_at: datetime = Field(default_factory=utcnow)

    author: User
    """The author who composed this comment."""

    stats: CommentStats | None = None
    """Statistics of the comment on the forum."""

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> datetime:
        return to_datetime(v)

    def dump(
        self, *, with_stats=False, with_author=False, exclude: set[str] | None = None
    ):
        """Model dump with minimal data."""
        exclude = {"stats", "author", *(exclude or set())}
        res = self.model_dump(mode="json", exclude=exclude)
        if with_author:
            res["author"] = self.author.dump()
        if with_stats and self.stats is not None:
            res["stats"] = self.stats.model_dump(mode="json")
        return res
