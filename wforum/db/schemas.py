from typing import Any, Literal

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, model_validator


class ResponseModel(BaseModel):
    status: Literal["OK", "FAILED"] = "OK"
    result: Any | None = None
    message: str | None = None


"""--------------------------------
|            AUTH APIs            |
--------------------------------"""


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username", "password", mode="before")
    def valid_nonempty_fields(cls, v) -> str:
        v = v.strip()
        if not v:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "username or password cannot be empty"
            )
        return v


class AgentInstructionSet(BaseModel):
    username: str
    instruction: str
    search_instruction: str | None = None

    @property
    def instruction_full(self):
        return self.instruction + (
            "" if self.search_instruction is None else "\n\n" + self.search_instruction
        )


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, v) -> str:
        v = v.strip()
        if not v:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "username field cannot be empty"
            )
        if len(v) < 3:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "username must be at least 3 characters"
            )
        return v

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, v) -> str:
        v = v.strip()
        if not v:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "password field cannot be empty"
            )
        if len(v) < 6:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "password must be at least 6 characters"
            )
        return v


"""---------------------------------
|            USERS APIs            |
---------------------------------"""


class UserPatchRequest(BaseModel):
    bio: str | None = None
    remove_avatar: bool = False
    avatar_url: str | None = None

    @model_validator(mode="after")
    def verify_request(self):
        if self.remove_avatar:
            if self.avatar_url is not None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Can't set avatar_url when remove_avatar is true.",
                )
        elif self.avatar_url is None and self.bio is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields to update")

        return self


"""----------------------------------
|            TOPICS APIs            |
----------------------------------"""


class TopicCreateRequest(BaseModel):
    topic_name: str
    description: str = ""

    @field_validator("topic_name", mode="before")
    @classmethod
    def valid_nonempty_fields(cls, v):
        v = v.strip()
        if not v:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "topic_name cannot be empty"
            )
        return v


"""---------------------------------
|            POSTS APIs            |
---------------------------------"""


class PostCreateRequest(BaseModel):
    title: str
    content: str
    topic_name: str | None = None

    @field_validator("title", "content", mode="before")
    @classmethod
    def valid_nonempty_fields(cls, v):
        v = v.strip()
        if not v:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "title or content cannot be empty"
            )
        return v


"""------------------------------------
|            COMMENTS APIs            |
------------------------------------"""


class CommentCreateRequest(BaseModel):
    content: str
    parent_id: str

    @field_validator("content", mode="before")
    @classmethod
    def valid_nonempty_fields(cls, v):
        v = v.strip()
        if not v:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "content field cannot be empty"
            )
        return v


"""---------------------------------
|            VOTES APIs            |
---------------------------------"""


class VoteCreateRequest(BaseModel):
    target_id: str
    vote_type: Literal["upvote", "downvote", "novote"]
