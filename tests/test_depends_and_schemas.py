from fastapi import status


def test_authenticated_endpoint_returns_current_user(client, forum_factory):
    forum_user = forum_factory.create_user("dep")
    response = client.get(
        "/users/me", headers=forum_factory.auth_headers(forum_user.token)
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["name"] == forum_user.user.name
    assert body["stats"] is not None


def test_protected_endpoint_requires_auth_header(client):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_comment_creation_rejects_blank_content(client, forum_factory):
    author = forum_factory.create_user("commenter")
    post = forum_factory.create_post(author=author)
    response = client.post(
        "/comments/",
        json={"parent_id": post.id, "content": "   "},
        headers=forum_factory.auth_headers(author.token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
