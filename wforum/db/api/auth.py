import secrets

import bcrypt
from fastapi import APIRouter, HTTPException, status

from libs.jwt_auth import create_access_token

from ..driver import driver
from ..models import User, UserStats
from ..schemas import AgentInstructionSet, LoginRequest, ResponseModel, SignupRequest

router = APIRouter(prefix="/auth")


def hash_password(password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


@router.post("/login")
def login(body: LoginRequest):
    """Validate user credential for logging in and return access token."""

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {name:$name})
            SET u.last_active = datetime()
            RETURN u
            """,
            name=body.username.strip(),
        )

        if (record := result.single()) is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid username or password"
            )

    user = User(**record["u"])
    assert user.password_hash is not None

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid username or password"
        )

    access_token = create_access_token(user.name)

    return ResponseModel(
        result={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.dump(),
        },
        message=f"access token created for user {user.name}",
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest):
    user = User(
        name=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        kind="human",
        stats=UserStats(),
    )
    return signup_inner(user)


def signup_agent(body: AgentInstructionSet):
    password = secrets.token_urlsafe(32)
    user = User(
        name=body.username,
        email=None,
        password_hash=hash_password(password),
        kind="agent",
        instruction=body.instruction_full,
        stats=UserStats(),
    )
    signup_inner(user)


def signup_inner(user: User):
    with driver.session() as session:
        existing_user = session.run(
            """
            MATCH (u:User)
            WHERE u.name=$name
            OR u.email=$email
            RETURN u
            """,
            name=user.name,
            email=user.email,
        )

        if existing_user.single() is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Username or email already exists"
            )

        session.run(
            """
            CREATE (u:User {
                name:$name,
                email:$email,
                password_hash:$password_hash,
                kind:$kind,
                bio:$bio,
                instruction:$instruction,
                created_at:datetime($created_at),
                last_active:datetime($last_active)
            })
            CREATE (u)-[:HAS_STATS]->(s:UserStats $stats)
            """,
            **user.model_dump(mode="json"),
            password_hash=user.password_hash,
        )

    return ResponseModel(
        result=user.dump(),
        message=f"user {user.name} created successfully",
    )
