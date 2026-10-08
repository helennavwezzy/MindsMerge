from fastapi import status


def test_post_creation_and_listing_by_topic(client, forum_factory):
    author = forum_factory.create_user("author")
    topic = forum_factory.create_topic("topic")

    post = forum_factory.create_post(author=author, topic=topic)

    posts_response = client.get(
        "/posts/", params={"topic_name": topic.name, "limit": 5}
    )
    assert posts_response.status_code == status.HTTP_200_OK
    assert any(p["id"] == post.id for p in posts_response.json())

    fetched = client.get(f"/posts/{post.id}")
    assert fetched.status_code == status.HTTP_200_OK
    fetched_body = fetched.json()
    assert fetched_body["topic"]["name"] == topic.name
    assert fetched_body["stats"]["num_comments"] == 0


def test_comment_reply_flow_and_notifications(client, forum_factory):
    author = forum_factory.create_user("author")
    commenter = forum_factory.create_user("commenter")
    topic = forum_factory.create_topic("topic")
    post = forum_factory.create_post(author=author, topic=topic)

    comment = forum_factory.create_comment(commenter, parent_id=post.id)
    post_after_comment_response = client.get(f"/posts/{post.id}")
    assert post_after_comment_response.status_code == status.HTTP_200_OK
    post_after_comment = post_after_comment_response.json()
    assert post_after_comment["stats"]["num_comments"] == 1

    reply = forum_factory.create_comment(
        author,
        parent_id=comment.id,
        content=f"{forum_factory.prefix}-reply",
    )
    refreshed_comment_response = client.get(f"/comments/{comment.id}")
    assert refreshed_comment_response.status_code == status.HTTP_200_OK
    refreshed_comment = refreshed_comment_response.json()
    assert refreshed_comment["stats"]["num_replies"] == 1

    post_comments_response = client.get(f"/posts/{post.id}/comments")
    assert post_comments_response.status_code == status.HTTP_200_OK
    post_comments = post_comments_response.json()
    assert comment.id in [c["id"] for c in post_comments]

    replies_response = client.get(f"/comments/{comment.id}/replies")
    assert replies_response.status_code == status.HTTP_200_OK
    replies = replies_response.json()
    assert [r["id"] for r in replies] == [reply.id]

    author_notifications = client.get(
        "/notification/", headers=forum_factory.auth_headers(author.token)
    )
    assert author_notifications.status_code == status.HTTP_200_OK
    author_data = author_notifications.json()
    assert post.id in author_data
    notified_post, notified_comments = author_data[post.id]
    assert notified_post["id"] == post.id
    assert [c["id"] for c in notified_comments] == [comment.id]

    commenter_notifications = client.get(
        "/notification/", headers=forum_factory.auth_headers(commenter.token)
    )
    assert commenter_notifications.status_code == status.HTTP_200_OK
    commenter_data = commenter_notifications.json()
    assert comment.id in commenter_data
    notified_comment, notified_replies = commenter_data[comment.id]
    assert notified_comment["id"] == comment.id
    assert [c["id"] for c in notified_replies] == [reply.id]


def test_mark_comment_as_read_hides_notifications(client, forum_factory):
    author = forum_factory.create_user("author")
    commenter = forum_factory.create_user("commenter")
    post = forum_factory.create_post(author=author)

    comment = forum_factory.create_comment(commenter, parent_id=post.id)

    author_notifications_response = client.get(
        "/notification/", headers=forum_factory.auth_headers(author.token)
    )
    assert author_notifications_response.status_code == status.HTTP_200_OK
    author_notifications = author_notifications_response.json()
    _, notified_comments = author_notifications[post.id]
    assert [c["id"] for c in notified_comments] == [comment.id]

    mark_response = client.post(
        "/comments/mark_as_read",
        json=[comment.id],
        headers=forum_factory.auth_headers(author.token),
    )
    assert mark_response.status_code == status.HTTP_200_OK
    cleared_notifications = client.get(
        "/notification/", headers=forum_factory.auth_headers(author.token)
    )
    assert cleared_notifications.status_code == status.HTTP_200_OK
    assert cleared_notifications.json() == {}

    reply = forum_factory.create_comment(author, parent_id=comment.id)
    commenter_notifications_response = client.get(
        "/notification/", headers=forum_factory.auth_headers(commenter.token)
    )
    assert commenter_notifications_response.status_code == status.HTTP_200_OK
    commenter_notifications = commenter_notifications_response.json()
    _, notified_replies = commenter_notifications[comment.id]
    assert [c["id"] for c in notified_replies] == [reply.id]

    mark_reply = client.post(
        "/comments/mark_as_read",
        json=[reply.id],
        headers=forum_factory.auth_headers(commenter.token),
    )
    assert mark_reply.status_code == status.HTTP_200_OK
    cleared_commenter = client.get(
        "/notification/", headers=forum_factory.auth_headers(commenter.token)
    )
    assert cleared_commenter.status_code == status.HTTP_200_OK
    assert cleared_commenter.json() == {}


def test_follow_topic_is_idempotent(client, forum_factory):
    user = forum_factory.create_user("follower")
    topic = forum_factory.create_topic("topic")

    follow_response = client.post(
        f"/topics/{topic.name}/follow",
        headers=forum_factory.auth_headers(user.token),
    )
    assert follow_response.status_code == status.HTTP_200_OK
    assert follow_response.json()["result"]["status"] == "followed"

    second_response = client.post(
        f"/topics/{topic.name}/follow",
        headers=forum_factory.auth_headers(user.token),
    )
    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.json()["result"]["status"] == "already followed"

    followed = client.get(
        "/topics/me/followed",
        headers=forum_factory.auth_headers(user.token),
    )
    assert followed.status_code == status.HTTP_200_OK
    assert [t["name"] for t in followed.json()] == [topic.name]
