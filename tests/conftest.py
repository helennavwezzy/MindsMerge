import uuid
from dataclasses import dataclass

import pytest
from fastapi import status
from fastapi.testclient import TestClient

import envy
from wforum.db.driver import driver
from wforum.db.models import Comment, Post, Topic, User
from wforum.db.run import app


@pytest.fixture(autouse=True)
def _reset_database():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    yield
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@dataclass
class ForumUser:
    user: User
    password: str
    token: str


class ForumFactory:
    """Helper for creating graph data through HTTP requests."""

    def __init__(self, client: TestClient):
        self.client = client
        self.prefix = f"test-{uuid.uuid4().hex[:8]}"
        self._admin_token: str | None = None

    def _unique(self, label: str) -> str:
        return f"{self.prefix}-{label}-{uuid.uuid4().hex[:6]}"

    def _auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def _login(self, username: str, password: str) -> str:
        response = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        return response.json()["result"]["access_token"]

    def _fetch_user(self, username: str) -> User:
        response = self.client.get(f"/users/{username}")
        assert response.status_code == status.HTTP_200_OK, response.text
        return User(**response.json())

    def _ensure_admin_token(self) -> str:
        if self._admin_token is not None:
            return self._admin_token

        username = envy.ADMIN_USERNAME
        password = "super-secret-admin"
        email = f"{self.prefix}-{username}@example.com"

        response = self.client.post(
            "/auth/signup",
            json={"username": username, "email": email, "password": password},
        )
        assert response.status_code in {
            status.HTTP_201_CREATED,
            status.HTTP_409_CONFLICT,
        }, response.text

        token = self._login(username, password)
        self._admin_token = token
        return token

    def auth_headers(self, token: str) -> dict[str, str]:
        return self._auth_headers(token)

    def create_user(self, label: str = "user") -> ForumUser:
        username = self._unique(label)
        email = f"{username}@example.com"
        password = f"{self.prefix}-{label}-pw"
        response = self.client.post(
            "/auth/signup",
            json={"username": username, "email": email, "password": password},
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text

        token = self._login(username, password)
        return ForumUser(
            user=self._fetch_user(username), password=password, token=token
        )

    def create_topic(self, label: str = "topic") -> Topic:
        token = self._ensure_admin_token()
        name = self._unique(label)
        response = self.client.post(
            "/topics/",
            json={
                "topic_name": name,
                "description": f"{name} description",
            },
            headers=self._auth_headers(token),
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        return Topic(**response.json()["result"])

    def get_post(self, post_id: str) -> Post:
        response = self.client.get(f"/posts/{post_id}")
        assert response.status_code == status.HTTP_200_OK, response.text
        return Post(**response.json())

    def get_comment(self, comment_id: str) -> Comment:
        response = self.client.get(f"/comments/{comment_id}")
        assert response.status_code == status.HTTP_200_OK, response.text
        return Comment(**response.json())

    def create_post(
        self,
        author: ForumUser,
        topic: Topic | None = None,
        title: str | None = None,
        content: str | None = None,
    ) -> Post:
        payload = {
            "title": title or f"{self.prefix}-post-{uuid.uuid4().hex[:4]}",
            "content": content or f"{self.prefix}-content",
            "topic_name": topic.name if topic else None,
        }
        response = self.client.post(
            "/posts/",
            json=payload,
            headers=self._auth_headers(author.token),
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        post_id = response.json()["result"]["id"]
        return self.get_post(post_id)

    def create_comment(
        self,
        author: ForumUser,
        parent_id: str,
        content: str | None = None,
    ) -> Comment:
        payload = {
            "content": content or f"{self.prefix}-comment-{uuid.uuid4().hex[:4]}",
            "parent_id": parent_id,
        }
        response = self.client.post(
            "/comments/",
            json=payload,
            headers=self._auth_headers(author.token),
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        comment_id = response.json()["result"]["id"]
        return self.get_comment(comment_id)


@pytest.fixture
def forum_factory(client: TestClient):
    return ForumFactory(client)
