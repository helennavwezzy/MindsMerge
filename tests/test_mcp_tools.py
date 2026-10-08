import uuid

import pytest
from fastapi import HTTPException, status

from wforum.db.models import Comment, Post
from wforum.db_mcp import mcp_tools


def test_full_discussion_until_returns_ordered_chain(forum_factory):
    author = forum_factory.create_user("author")
    commenter = forum_factory.create_user("commenter")

    post = forum_factory.create_post(author=author)
    c1 = forum_factory.create_comment(commenter, parent_id=post.id)

    # unrelated comment on the same post
    forum_factory.create_comment(author, parent_id=post.id)

    c2 = forum_factory.create_comment(author, parent_id=c1.id)
    # unrelated reply to c1
    forum_factory.create_comment(author, parent_id=c1.id)

    c3 = forum_factory.create_comment(commenter, parent_id=c2.id)
    # unrelated reply to c2
    forum_factory.create_comment(author, parent_id=c2.id)

    chain = mcp_tools.get_full_discussion_until(c3.id)

    assert [type(node) for node in chain] == [Post, Comment, Comment, Comment]
    assert [node.id for node in chain] == [post.id, c1.id, c2.id, c3.id]
    assert [node.author.name for node in chain] == [
        author.user.name,
        commenter.user.name,
        author.user.name,
        commenter.user.name,
    ]


def test_full_discussion_until_missing_comment_raises_404():
    with pytest.raises(HTTPException) as exc:
        mcp_tools.get_full_discussion_until(uuid.uuid4().hex)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
