import uuid

from fastapi import status


def test_signup_and_login_roundtrip(client):
    username = f"member-{uuid.uuid4().hex[:6]}"
    password = "secret42"
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    assert signup_response.status_code == status.HTTP_201_CREATED
    signup_data = signup_response.json()["result"]
    assert signup_data["name"] == username
    assert signup_data["email"] == f"{username}@example.com"

    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()["result"]
    assert login_data["user"]["name"] == username
    assert login_data["token_type"] == "bearer"
    assert "password_hash" not in login_data["user"]

    bad_login = client.post(
        "/auth/login",
        json={"username": username, "password": f"{password}x"},
    )
    assert bad_login.status_code == status.HTTP_401_UNAUTHORIZED


def test_patch_user_updates_profile(client, forum_factory):
    forum_user = forum_factory.create_user("profile")
    new_bio = f"{forum_factory.prefix}-new-bio"
    new_avatar = f"https://example.com/{forum_factory.prefix}.png"

    patch_response = client.patch(
        "/users/me",
        json={"bio": new_bio, "avatar_url": new_avatar},
        headers=forum_factory.auth_headers(forum_user.token),
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.json()["result"]["bio"] == new_bio
    assert patch_response.json()["result"]["avatar_url"] == new_avatar

    refreshed = client.get(f"/users/{forum_user.user.name}")
    assert refreshed.status_code == status.HTTP_200_OK
    refreshed_body = refreshed.json()
    assert refreshed_body["bio"] == new_bio
    assert refreshed_body["avatar_url"] == new_avatar


def test_user_patch_validator_rejects_conflicting_fields(client, forum_factory):
    forum_user = forum_factory.create_user("conflict")
    response = client.patch(
        "/users/me",
        json={"remove_avatar": True, "avatar_url": "https://example.com/a.png"},
        headers=forum_factory.auth_headers(forum_user.token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
