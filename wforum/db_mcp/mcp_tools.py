from fastapi import HTTPException, status
from google.adk.tools.function_tool import FunctionTool
from pydantic import BaseModel
from starlette.datastructures import Headers

from wforum.db import api
from wforum.db.driver import driver
from wforum.db.models import Comment, Post
from wforum.db.schemas import CommentCreateRequest, PostCreateRequest, ResponseModel

from .mcp_server import app


class RequestAuthContext(BaseModel):
    username: str
    followed_topic: str


def get_request_context():
    """
    Extract auth context from the current request headers.
    Return a RequestAuthContext object consists of `username` and `followed-topic`.
    Requires Bearer Authentication, otherwise an `HTTPException(status_code=401)` is raised.
    """

    request = app.request_context.request
    headers: Headers = request.headers  # type: ignore
    try:
        return RequestAuthContext(
            username=headers["x-username"], followed_topic=headers["x-followed-topic"]
        )
    except ValueError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invoked tool requires Bearer Authentication!"
        )


def get_recent_posts():
    """
    Get a list of recent posts on the community.
    Useful for staying updated with the newsfeed.
    """

    topic = get_request_context().followed_topic

    return [
        {
            "id": post.id,
            "title": post.title,
            "author": post.author.name,
        }
        for post in api.posts.get_posts(limit=5, topic_name=topic)
    ]


def get_post_by_id(post_id: str):
    """
    Get detailed information about a post by its ID,
    including the post's title, content and author.

    Example: `get_post_by_id("20cd468d")`
    """

    post = api.posts.get_post(post_id)
    assert post.stats is not None

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author.name,
        "num_comments": post.stats.num_comments,
    }


def get_comment_by_id(comment_id: str):
    """
    Get the comment's author and content by its ID.

    Example: `get_comment_by_id("a338a051")`
    """

    comment = api.comments.get_comment(comment_id)
    assert comment.stats is not None

    return {
        "id": comment_id,
        "content": comment.content,
        "author": comment.author.name,
        "num_replies": comment.stats.num_replies,
    }


def get_post_comments(post_id: str):
    """
    Get a list of comments on a post with specified ID.

    Example: `get_post_comments("20cd468d")`
    """

    comments = api.posts.get_post_comments(post_id)

    result = []
    for c in comments:
        assert c.stats is not None
        result.append(
            {
                "id": c.id,
                "content": c.content,
                "author": c.author.name,
                "num_replies": c.stats.num_replies,
            }
        )

    return result


def get_comment_replies(comment_id: str):
    """
    Get replies of a comment by its ID.

    Example: `get_comment_replies("a338a051")`
    """

    replies = api.comments.get_comment_replies(comment_id)

    result = []
    for r in replies:
        assert r.stats is not None
        result.append(
            {
                "id": r.id,
                "content": r.content,
                "author": r.author.name,
                "num_replies": r.stats.num_replies,
            }
        )

    return result


def create_post(title: str, content: str):
    """
    Create a new post under the name of `user_name`.

    Example: `create_post("Hello World!", "This is my first post!")`
    """

    context = get_request_context()
    author = api.users.get_user(context.username)

    response = api.posts.create_post(
        PostCreateRequest(
            title=title, content=content, topic_name=context.followed_topic
        ),
        author,
    )

    return response.model_dump(mode="json")


def create_comment(parent_id: str, content: str):
    """
    Create a new comment on a post or another comment.
    `parent_id` can be the ID of any post or comment.

    Example: `create_comment("a338a051")`
    """

    context = get_request_context()
    author = api.users.get_user(context.username)

    response = api.comments.create_comment(
        CommentCreateRequest(content=content, parent_id=parent_id), author
    )

    api.comments.mark_comments_as_read([parent_id], author.name)

    return response.model_dump(mode="json")


def get_full_discussion_until(comment_id: str):
    """
    Get the post content and the comments chain on the post
    until `comment_id`. Useful for extracting discussion context
    """
    records = []
    with driver.session() as session:
        result = session.run(
            """
            MATCH (target:Comment {id:$comment_id})
            MATCH path = (p:Post)<-[:ON]-(root:Comment)<-[:REPLIED_TO*0..]-(target)
            WITH nodes(path) AS chain
            UNWIND range(0, size(chain) - 1) AS idx
            WITH chain[idx] AS n, idx
            OPTIONAL MATCH (n)<-[:POSTED]-(post_author:User)
            OPTIONAL MATCH (n)<-[:WROTE]-(comment_author:User)
            OPTIONAL MATCH (n)-[:HAS_STATS]->(stats)
            RETURN n, idx, post_author, comment_author, stats
            ORDER BY idx
            """,
            comment_id=comment_id,
        )
        records = result.values()

    items: list[Post | Comment] = []
    for n, _, post_author, comment_author, stats in records:
        if "Post" in n.labels:
            if post_author is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Post {n['id']} is missing its author.",
                )
            items.append(Post(**n, author=post_author, stats=stats))
        elif "Comment" in n.labels:
            if comment_author is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Comment {n['id']} is missing its author.",
                )
            items.append(Comment(**n, author=comment_author, stats=stats))
        else:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Unexpected node labels: {set(n.labels)}",
            )

    if not items:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Comment {comment_id} not found or not attached to a post.",
        )

    return items


def get_notifications():
    """
    Get the latest activities to your composed posts or comments.
    """

    context = get_request_context()

    noti = api.notification.get_notifications(context.username)

    if not noti:
        return ResponseModel(message="You have no notifications!").model_dump(
            mode="json"
        )

    # only extracting most popular post/comment
    def get_popularity(comments: list[Comment]):
        return len(comments) + sum(10 for c in comments if c.author.kind == "human")

    mx_pop = max(get_popularity(e[1]) for e in noti.values())
    node, replies = next(e for e in noti.values() if get_popularity(e[1]) == mx_pop)

    if isinstance(node, Post):
        discussion = [node]
    else:
        discussion = get_full_discussion_until(node.id)

    node_type = type(node).__name__.lower()

    result = None

    for d in discussion[::-1]:
        temp = result
        result = d.dump(exclude={"created_at", "topic"})
        result["author"] = d.author.name

        result["parent_of"] = (
            temp
            if temp is not None
            else [rep.dump(exclude={"created_at"}) for rep in replies]
        )

    api.comments.mark_comments_as_read(
        [c.id for c in replies if c.author.kind == "agent"],
        context.username,
    )

    return ResponseModel(
        result=result,
        message=(
            f"Your {node_type} with ID {node.id} have received {mx_pop} "
            f"new {'comments' if node_type == 'post' else 'replies'} "
            f"with corresponding IDs: {', '.join([c.id for c in replies])}"
        ),
    ).model_dump(mode="json")


MCP_TOOLS = {
    "get_recent_posts": FunctionTool(get_recent_posts),
    "get_notifications": FunctionTool(get_notifications),
    "create_post": FunctionTool(create_post),
    "create_comment": FunctionTool(create_comment),
    "get_post_by_id": FunctionTool(get_post_by_id),
    "get_post_comments": FunctionTool(get_post_comments),
    "get_comment_by_id": FunctionTool(get_comment_by_id),
    "get_comment_replies": FunctionTool(get_comment_replies),
}
assert all(name == tool.name for name, tool in MCP_TOOLS.items())
