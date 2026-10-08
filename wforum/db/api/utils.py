from fastapi import HTTPException, status

from wforum.db.driver import driver


def get_node_label(target_id: str) -> str:
    with driver.session() as session:
        result = session.run(
            """
            MATCH (n {id:$target_id})
            RETURN labels(n) AS labels
            """,
            target_id=target_id,
        )

        if (record := result.single()) is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"No node of ID {target_id} can be found!",
            )

    labels = record["labels"]
    assert len(labels) == 1
    return labels[0]
