from fastapi import APIRouter, Depends

from ..depends import get_current_username
from ..driver import driver
from ..models import Comment, Post

router = APIRouter(prefix="/notification")


@router.get("/")
def get_notifications(username=Depends(get_current_username)):
    with driver.session() as session:
        records = session.run(
            """
            MATCH (u1:User {name: $username})-[:WROTE|POSTED]->(p)
            MATCH (u2:User)-[:WROTE]->(c:Comment)-[:ON|REPLIED_TO]->(p)
            WHERE u2.name <> u1.name

            OPTIONAL MATCH (u1)-[r:READ]->(c)
            MATCH (c)-[:HAS_STATS]->(s:CommentStats)

            WITH u1, p, c, s, u2, r
            WHERE r IS NULL

            RETURN u1, p, c, s, u2
            """,
            username=username,
        )

        result: dict[str, tuple[Post | Comment, list[Comment]]] = {}
        for record in records:
            p_id = record["p"]["id"]
            if p_id not in result:
                if "Post" in record["p"].labels:
                    result[p_id] = (Post(**record["p"], author=record["u1"]), [])
                elif "Comment" in record["p"].labels:
                    result[p_id] = (Comment(**record["p"], author=record["u1"]), [])
                else:
                    raise ValueError(f"Invalid node: {record['p'].labels}")

            result[p_id][1].append(
                Comment(
                    **record["c"],
                    stats=record["s"],
                    author=record["u2"],
                )
            )

        return result
