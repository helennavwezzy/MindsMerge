from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from ..depends import get_current_username
from ..driver import driver
from ..models import Comment, Post, User
from ..schemas import ResponseModel, VoteCreateRequest
from .utils import get_node_label

router = APIRouter(prefix="/votes")


@router.get("/")
def get_vote_status(
    target_id: str,
    target_type: Literal["Post", "Comment"],
    username: str = Depends(get_current_username),
):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {name:$name})
            MATCH (t:%s {id:$target_id})-[:HAS_STATS]->(s:%sStats)
            OPTIONAL MATCH (u)-[r1:UPVOTED]->(t)
            OPTIONAL MATCH (u)-[r2:DOWNVOTED]->(t)
            RETURN r1, s, r2
            """
            % (target_type, target_type),
            name=username,
            target_id=target_id,
        )

        if (record := result.single()) is None:
            # TODO (glowo): This is a silly assumption!
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Node {target_type} of ID {target_id} not found!",
            )

    if record["r1"] is not None:
        user_vote = "upvoted"
    elif record["r2"] is not None:
        user_vote = "downvoted"
    else:
        user_vote = "not voted"

    return {**record["s"], "user_vote": user_vote}


@router.post("/")
def create_vote(body: VoteCreateRequest, username: str = Depends(get_current_username)):
    equiv = {
        "upvote": "upvoted",
        "downvote": "downvoted",
        "novote": "not voted",
    }

    target_type = get_node_label(body.target_id)
    assert target_type in ("Post", "Comment")
    vote_status = get_vote_status(body.target_id, target_type, username)

    if equiv[body.vote_type] == vote_status["user_vote"]:
        return ResponseModel(
            message=f"user already {vote_status['user_vote']}",
        )

    # match the user, the target (post/comment) and the target's author
    header_cyp = """
        MATCH (u2:User {name:$name})
        MATCH (u1:User)-[:%s]->(p:%s {id:$target_id})-[:HAS_STATS]->(target_stats:%sStats)
        MATCH (u1)-[:HAS_STATS]->(user_stats)
    """ % (
        "POSTED" if target_type == "Post" else "WROTE",
        target_type,
        target_type,
    )

    kwargs = {"target_id": body.target_id, "name": username}

    with driver.session() as session:
        # step 1: check request validity
        res1 = session.run(header_cyp + "\nRETURN u2", kwargs).single()
        if res1 is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "invalid request, but we're too dogshit to know why",
            )

        # step 2: remove previous vote
        session.run(
            """
            %s
            OPTIONAL MATCH (u2)-[r:UPVOTED]->(p)
            WITH user_stats, target_stats, r
            WHERE r IS NOT NULL
            SET user_stats.karma = user_stats.karma - 1,
                target_stats.upvotes = target_stats.upvotes - 1
            DELETE r
            """
            % header_cyp,
            kwargs,
        )
        session.run(
            """
            %s
            OPTIONAL MATCH (u2)-[r:DOWNVOTED]->(p)
            WITH user_stats, target_stats, r
            WHERE r IS NOT NULL
            SET user_stats.karma = user_stats.karma + 1,
                target_stats.downvotes = target_stats.downvotes - 1
            DELETE r
            """
            % header_cyp,
            kwargs,
        )

        # step 3: update new vote
        match body.vote_type:
            case "novote":
                cyp = """
                    %s
                    RETURN u1, p, user_stats, target_stats
                """
            case "upvote":
                cyp = """
                    %s
                    MERGE (u2)-[r:UPVOTED]->(p)
                    SET user_stats.karma = user_stats.karma + 1,
                        target_stats.upvotes = target_stats.upvotes + 1
                    RETURN u1, p, user_stats, target_stats
                """
            case "downvote":
                cyp = """
                    %s
                    MERGE (u2)-[r:DOWNVOTED]->(p)
                    SET user_stats.karma = user_stats.karma - 1,
                        target_stats.downvotes = target_stats.downvotes + 1
                    RETURN u1, p, user_stats, target_stats
                """

        res2 = session.run(cyp % header_cyp, kwargs).single()
        assert res2 is not None

    match target_type:
        case "Post":
            res = Post(
                **res2["p"],
                author=User(**res2["u1"], stats=res2["user_stats"]),
                stats=res2["target_stats"],
            )
        case "Comment":
            res = Comment(
                **res2["p"],
                author=User(**res2["u1"], stats=res2["user_stats"]),
                stats=res2["target_stats"],
            )

    return ResponseModel(
        result=res,
        message=f"user {equiv[body.vote_type]} successfully",
    )
