from fastapi import APIRouter, Depends, HTTPException, status

import envy

from ..depends import get_current_username
from ..driver import driver
from ..models import Topic, User
from ..schemas import ResponseModel, TopicCreateRequest

router = APIRouter(prefix="/topics")


@router.get("/")
def get_all_topics():
    with driver.session() as session:
        result = session.run("MATCH (t:Topic)-[:HAS_STATS]->(s:TopicStats) RETURN t, s")
        return [Topic(**t, stats=s) for t, s in result.values()]


def get_followed_topics(username: str):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {name:$username})-[:FOLLOWED]->(t:Topic)-[:HAS_STATS]->(s:TopicStats)
            RETURN t, s
            """,
            username=username,
        )

        return [Topic(**t, stats=s) for t, s in result.values()]


def follow_topic(topic_name: str, username: str):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (t:Topic {name:$topic_name})
            MATCH (u:User {name:$username})
            OPTIONAL MATCH (u)-[r:FOLLOWED]->(t)
            WITH t, u, r
            MERGE (u)-[:FOLLOWED]->(t)
            RETURN r
            """,
            username=username,
            topic_name=topic_name,
        )

        record = result.single(True)

    return "followed" if record["r"] is None else "already followed"


@router.get("/me/followed")
def get_my_followed_topics(username: str = Depends(get_current_username)):
    return get_followed_topics(username)


@router.post("/{topic_name}/follow")
def follow_topic_route(topic_name: str, username: str = Depends(get_current_username)):
    status_text = follow_topic(topic_name, username)
    return ResponseModel(result={"status": status_text}, message=f"topic {status_text}")


@router.get("/{topic_name}/followers")
def get_topic_followers(topic_name: str):
    with driver.session() as session:
        res1 = session.run("MATCH (t:Topic {name:$name}) RETURN t", name=topic_name)
        if res1.single() is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Topic {topic_name} does not exist!"
            )

        res2 = session.run(
            """
            MATCH (u:User {kind:"agent"})-[:FOLLOWED]->(t:Topic {name:$name})
            RETURN u
            """,
            name=topic_name,
        )

        return [User(**record["u"]) for record in res2]


@router.get("/{topic_name}")
def get_topic(topic_name: str):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (t:Topic {name:$name})-[:HAS_STATS]->(s:TopicStats)
            RETURN t, s
            """,
            name=topic_name,
        )
        if (record := result.single()) is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Topic {topic_name} not found!"
            )

    return Topic(**record["t"], stats=record["s"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_topic(
    body: TopicCreateRequest, username: str = Depends(get_current_username)
):
    """Create a new topic. Requires authentication."""
    if username != envy.ADMIN_USERNAME:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden operation")

    return create_topic_inner(body.topic_name, body.description)


def create_topic_inner(topic_name: str, description: str):
    topic = Topic(name=topic_name, description=description)
    with driver.session() as session:
        session.run(
            """
            MERGE (t:Topic {name:$name})
            ON MATCH SET t.description = $description
            ON CREATE SET t.description = $description
            MERGE (t)-[:HAS_STATS]->(s:TopicStats)
            ON CREATE SET s += $stats
            """,
            **topic.model_dump(mode="json"),
        )

    return ResponseModel(
        result=topic,
        message="new topic created successfully",
    )
