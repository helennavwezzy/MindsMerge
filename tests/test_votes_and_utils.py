import uuid

from fastapi import status


def test_vote_status_and_toggle_updates_stats(client, forum_factory):
    author = forum_factory.create_user("author")
    voter = forum_factory.create_user("voter")
    post = forum_factory.create_post(author=author)

    initial_status_response = client.get(
        "/votes/",
        params={"target_id": post.id, "target_type": "Post"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert initial_status_response.status_code == status.HTTP_200_OK
    initial_status = initial_status_response.json()
    assert initial_status["user_vote"] == "not voted"
    assert initial_status["upvotes"] == 0
    assert initial_status["downvotes"] == 0

    upvote_response = client.post(
        "/votes/",
        json={"target_id": post.id, "vote_type": "upvote"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert upvote_response.status_code == status.HTTP_200_OK
    voted_post = upvote_response.json()["result"]
    assert voted_post["stats"]["upvotes"] == 1
    assert voted_post["stats"]["downvotes"] == 0

    upvoted_status = client.get(
        "/votes/",
        params={"target_id": post.id, "target_type": "Post"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert upvoted_status.status_code == status.HTTP_200_OK
    assert upvoted_status.json()["user_vote"] == "upvoted"

    repeat_upvote = client.post(
        "/votes/",
        json={"target_id": post.id, "vote_type": "upvote"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert repeat_upvote.status_code == status.HTTP_200_OK
    repeat_status_response = client.get(
        "/votes/",
        params={"target_id": post.id, "target_type": "Post"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert repeat_status_response.status_code == status.HTTP_200_OK
    repeat_status = repeat_status_response.json()
    assert repeat_status["upvotes"] == 1

    downvote_response = client.post(
        "/votes/",
        json={"target_id": post.id, "vote_type": "downvote"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert downvote_response.status_code == status.HTTP_200_OK
    downvoted_post = downvote_response.json()["result"]
    assert downvoted_post["stats"]["downvotes"] == 1
    assert downvoted_post["stats"]["upvotes"] == 0
    downvoted_status = client.get(
        "/votes/",
        params={"target_id": post.id, "target_type": "Post"},
        headers=forum_factory.auth_headers(voter.token),
    )
    assert downvoted_status.status_code == status.HTTP_200_OK
    assert downvoted_status.json()["user_vote"] == "downvoted"

    author_response = client.get(f"/users/{author.user.name}")
    assert author_response.status_code == status.HTTP_200_OK
    author_stats = author_response.json()["stats"]
    assert author_stats["karma"] == -1


def test_get_node_label_missing_raises(client, forum_factory):
    user = forum_factory.create_user("reader")
    response = client.get(
        "/votes/",
        params={"target_id": uuid.uuid4().hex, "target_type": "Post"},
        headers=forum_factory.auth_headers(user.token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
