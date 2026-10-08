import asyncio

from wforum.db import api

from .gen_agents import GenAgentsPrep
from .gen_topics import GenTopicsPrep
from .summarize_agents import SummarizeAgentsPrep


async def main():
    # =========================
    #   Generate a few topics
    # =========================

    # await GenTopicsPrep(
    #     "Valorant", "I want to create a community for Valorant players"
    # ).run()

    await GenTopicsPrep(
        "DontStarveTogether",
        "I want to create a community for the Don't Starve Together game",
    ).run()

    # await GenTopicsPrep(
    #     "TheBackrooms",
    #     "I want to create a community for The Backrooms (ref: https://backrooms-wiki.wikidot.com)",
    # ).run()

    # await GenTopicsPrep(
    #     "MachineLearning",
    #     "I want to create a community `MachineLearning` for the ML/DL analysts/researchers",
    # ).run()

    # await GenTopicsPrep(
    #     "LofiAndChill",
    #     "I want to have a community `LofiAndChill`, where we can share lofi music and chill out"
    # ).run()

    # ==============================================
    #   Generate agents instructions and summaries
    # ==============================================

    target_topic = "DontStarveTogether"
    topic = api.topics.get_topic(target_topic)

    query = (
        f"Suggest a list of 5 active agents for the community: r/{topic.name}.\n"
        f"Introduction: {topic.description}"
    )

    await GenAgentsPrep(topic.name).run(query)
    await SummarizeAgentsPrep(topic.name).run()


if __name__ == "__main__":
    asyncio.run(main())
