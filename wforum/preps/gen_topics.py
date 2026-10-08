import json

from google.adk.events import Event

from libs.agents import CustomAgentRunner
from libs.agents.helpers import crunch, handle_adk_event
from wforum.db import api

from ..agents import TopicCreationResult, topic_creator_agent


def _custom_handle_adk_event(event: Event):
    if event.is_final_response():
        assert event.content is not None
        assert event.content.parts
        text = event.content.parts[0].text
        assert text is not None
        return TopicCreationResult(**json.loads(text))
    else:
        handle_adk_event(event)


def _display_result(topic: TopicCreationResult):
    crunch("📍 New topic:", topic.model_dump_json(indent=2))


class GenTopicsPrep:
    def __init__(self, topic_name: str, query: str):
        self.topic_name = topic_name
        self.runner = CustomAgentRunner(
            sqlite_uri="data/prep_data.db",
            agent=topic_creator_agent,
            user_id="gen_topics_prep",
            session_id=topic_name,
        )
        self.query = query

    async def run(self):
        if await self.runner.get_session() is None:
            await self._generate()
        else:
            crunch(
                "⏭️ Skipping topics generation for topic "
                f"`{self.topic_name}`: session already exists!"
            )

        await self._merge_saved_topics()

    async def _generate(self):
        # Send each query under the session
        crunch("🧑 User:", self.query)

        result: TopicCreationResult | None = None

        async for event in self.runner.run(self.query):
            r = _custom_handle_adk_event(event)
            if r is not None:
                assert result is None
                assert r.topic_name == self.topic_name
                result = r

        assert result is not None
        _display_result(result)

        await self.runner.update_session_state(
            {"generated_topic": result.model_dump(mode="json")}
        )

    async def _merge_saved_topics(self):
        session = await self.runner.get_session()
        assert session is not None

        data = session.state["generated_topic"]
        topic = TopicCreationResult(**data)

        api.topics.create_topic_inner(topic.topic_name, topic.description)
        crunch(f"✅ Topic node {topic.topic_name} successfully created!")
