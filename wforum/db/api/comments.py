from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..depends import get_current_user, get_current_username
from ..driver import driver
from ..models import Comment, CommentStats, Post, User
from ..schemas import CommentCreateRequest, ResponseModel
from .utils import get_node_label

router = APIRouter(prefix="/comments")


@router.get("/")
def get_comments(page: int = 0, limit: int = 5, topic_name: str | None = None):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u1:User)-[:WROTE]->(c:Comment)-[:ON]->(p:Post)<-[:POSTED]-(u2:User)
            MATCH (c)-[:HAS_STATS]->(s:CommentStats)
            OPTIONAL MATCH (p)-[:HAS_TOPIC]->(t:Topic)
            WITH u1, u2, c, p, s, t
            WHERE $topic_name IS NULL OR t.name = $topic_name
            ORDER BY c.created_at DESC
            SKIP $skip
            LIMIT $limit
            RETURN u1, u2, c, p, s, t
            """,
            topic_name=topic_name,
            skip=page * limit,
            limit=limit,
        )

        return [
            {
                "parent": Post(
                    **p,
                    author=u2,
                    topic=t,
                ),
                "comment": Comment(**c, author=u1, stats=s),
            }
            for u1, u2, c, p, s, t in result.values()
        ]


@router.get("/{comment_id}")
def get_comment(comment_id: str):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)-[:WROTE]->(c:Comment {id:$id})-[:HAS_STATS]->(s:CommentStats)
            RETURN u, c, s
            """,
            id=comment_id,
        )

        if (record := result.single()) is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"No comment with id {comment_id} can be found.",
            )

    return Comment(
        **record["c"],
        author=record["u"],
        stats=record["s"],
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_comment(
    body: CommentCreateRequest, author: User = Depends(get_current_user)
):
    parent_type = get_node_label(body.parent_id)

    match parent_type:
        case "Post":
            rel = "ON"
            cypher = """
            MATCH (p:Post {id:$parent_id})-[:HAS_STATS]->(s1:PostStats)
            SET s1.num_comments = s1.num_comments + 1
            """
        case "Comment":
            rel = "REPLIED_TO"
            cypher = """
            MATCH (p:Comment {id:$parent_id})-[:HAS_STATS]->(s1:CommentStats)
            SET s1.num_replies = s1.num_replies + 1
            """
        case _:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid parent_type {parent_type} for comment.",
            )

    comment = Comment(
        author=author,
        content=body.content,
        stats=CommentStats(),
    )

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {name:$author_name})
            %s
            CREATE (u)-[:WROTE]->(c:Comment {
                id:$id,
                content:$content,
                created_at:datetime($created_at)
            })-[:%s]->(p)
            CREATE (c)-[:HAS_STATS]->(s2:CommentStats $stats)
            RETURN c
            """
            % (cypher, rel),
            author_name=author.name,
            parent_id=body.parent_id,
            **comment.model_dump(mode="json", exclude={"author"}),
        )

        if result.single() is None:
            # TODO (glowo): this is a silly assumption!
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"No {parent_type} parent with ID {body.parent_id} found",
            )

    return ResponseModel(
        result=comment.dump(exclude={"content"}),
        message="new comment created successfully",
    )


@router.get("/{comment_id}/replies")
def get_comment_replies(comment_id: str):
    """Get all replies for a comment."""

    with driver.session() as session:
        # Check if the comment exists
        r1 = session.run("MATCH (c:Comment {id:$id}) RETURN c.id", id=comment_id)
        if r1.single() is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Comment with ID {comment_id} not found!"
            )

        # Fetching replies
        r2 = session.run(
            """
            MATCH (u:User)-[:WROTE]->(c:Comment)-[:REPLIED_TO]->(:Comment {id:$id})
            MATCH (c:Comment)-[:HAS_STATS]->(s:CommentStats)
            RETURN u, c, s
            ORDER BY c.created_at
            """,
            id=comment_id,
        )

        # Return from result
        return [Comment(**c, stats=s, author=u) for u, c, s in r2.values()]


class MarkCommentsReadRequest(BaseModel):
    comment_ids: list[str]


@router.post("/mark_as_read")
def mark_comments_as_read(
    comment_ids: list[str], username: str = Depends(get_current_username)
):
    """Mark a list of comments as read for the user in one Cypher."""

    if len(comment_ids) == 0:
        return ResponseModel(message="No comment ids provided")

    ids = list(set(comment_ids))
    with driver.session() as session:
        session.run(
            """
            MATCH (u:User {name:$username})
            UNWIND $comment_ids AS cid
            MATCH (c:Comment {id:cid})
            MERGE (u)-[:READ]->(c)
            """,
            username=username,
            comment_ids=ids,
        )

    return ResponseModel(
        message=f"Marked {len(ids)} comment(s) as read by user {username}"
    )
