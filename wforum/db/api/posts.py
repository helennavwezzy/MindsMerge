from fastapi import APIRouter, Depends, HTTPException, status

from ..depends import get_current_user
from ..driver import driver
from ..models import Comment, Post, PostStats, User
from ..schemas import PostCreateRequest, ResponseModel
from .topics import get_topic

router = APIRouter(prefix="/posts")


@router.get("/")
def get_posts(page: int = 0, limit: int = 10, topic_name: str | None = None):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)-[:POSTED]->(p:Post)
            MATCH (p)-[:HAS_STATS]->(s:PostStats)
            OPTIONAL MATCH (p)-[:HAS_TOPIC]->(t:Topic)
            WITH u, p, s, t
            WHERE $topic_name IS NULL OR t.name = $topic_name
            ORDER BY p.created_at DESC
            SKIP $skip
            LIMIT $limit
            RETURN u, p, s, t
            """,
            topic_name=topic_name,
            skip=page * limit,
            limit=limit,
        )

        return [Post(**p, author=u, topic=t, stats=s) for u, p, s, t in result.values()]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(body: PostCreateRequest, author: User = Depends(get_current_user)):
    """Create a new post. Requires authentication."""

    post = Post(
        title=body.title,
        content=body.content,
        author=author,
        topic=get_topic(body.topic_name) if body.topic_name else None,
        stats=PostStats(),
    )

    with driver.session() as session:
        session.run(
            """
            MATCH (u:User {name:$author_name})
            CREATE (u)-[:POSTED]->(p:Post {
                id:$id,
                title:$title,
                content:$content,
                created_at:datetime($created_at)
            })-[:HAS_STATS]->(s:PostStats $stats)
            """,
            author_name=post.author.name,
            **post.model_dump(mode="json", exclude={"topic", "author"}),
        )

        if post.topic is not None:
            session.run(
                """
                MATCH (p:Post {id:$post_id})
                MATCH (t:Topic {name:$topic_name})
                MERGE (p)-[:HAS_TOPIC]->(t)
                """,
                post_id=post.id,
                topic_name=post.topic.name,
            )

    return ResponseModel(
        result=post.dump(exclude={"content", "topic"}),
        message="new post created successfully",
    )


@router.get("/{post_id}")
def get_post(post_id: str):
    """Get a single post by ID."""

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)-[:POSTED]->(p:Post {id:$id})-[:HAS_STATS]->(s:PostStats)
            OPTIONAL MATCH (p)-[:HAS_TOPIC]->(t:Topic)
            RETURN u, p, s, t
            """,
            id=post_id,
        )

        if (record := result.single()) is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Post with ID {post_id} not found!"
            )

    return Post(
        **record["p"],
        author=record["u"],
        stats=record["s"],
        topic=record["t"],
    )


@router.get("/{post_id}/comments")
def get_post_comments(post_id: str):
    """Get the list of all comments for a post."""

    with driver.session() as session:
        # Check if post with ID of post_id exists
        r1 = session.run("MATCH (p:Post {id:$post_id}) RETURN p.id", post_id=post_id)
        if r1.single() is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Post with ID {post_id} not found!"
            )

        # Fetching comments
        r2 = session.run(
            """
            MATCH (u:User)-[:WROTE]->(c:Comment)-[:ON]->(:Post {id:$id})
            MATCH (c)-[:HAS_STATS]->(s:CommentStats)
            RETURN u, c, s
            ORDER BY c.created_at DESC
            """,
            id=post_id,
        )

        # Return from result
        return [Comment(**c, stats=s, author=u) for u, c, s in r2.values()]
