import asyncio
import sys

from libs.agents.helpers import crunch
from wforum.agents import ContentCreatorRunner
from wforum.db import api


async def main():
    topic = api.topics.get_topic(sys.argv[1])
    followers = api.topics.get_topic_followers(topic.name)

    agents = {
        follower.name: ContentCreatorRunner(
            topic=topic,
            agent_user=follower,
        )
        for follower in followers
    }

    while True:
        crunch(
            "\n========================================",
            f"{'⛅ New time step BEGINS':^40}",
            "========================================",
        )

        for agent in agents.values():
            await agent.step()

        crunch(
            "========================================",
            f"{'⛅ END of time step':^40}",
            "========================================",
        )

        # Ask if user wants to continue
        answer = input("Continue? (y/n): ")
        if answer.lower() != "y":
            break


if __name__ == "__main__":
    asyncio.run(main())
