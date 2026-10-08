import json

from fastapi import HTTPException
from google.adk.events import Event

from libs.agents import CustomAgentRunner
from libs.agents.helpers import crunch, handle_adk_event
from wforum.agents import AgentsCreationResult, agent_creator_agent
from wforum.db import api


def _custom_handle_adk_event(event: Event):
    if event.is_final_response():
        assert event.content is not None
        assert event.content.parts
        text = event.content.parts[0].text
        assert text is not None
        return AgentsCreationResult(**json.loads(text))
    else:
        handle_adk_event(event)


def _display_result(result: AgentsCreationResult):
    for i, created_agent in enumerate(result.result, 1):
        crunch(f"🥷 Agent {i}:", created_agent)


class GenAgentsPrep:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.runner = CustomAgentRunner(
            sqlite_uri="data/prep_data.db",
            agent=agent_creator_agent,
            user_id="gen_agents_prep",
            session_id=topic_name,
        )
        self.result: AgentsCreationResult

    async def run(self, query: str):
        if await self.runner.get_session() is None:
            await self._generate(query)
        else:
            crunch(
                "⏭️ Skipping agents generation for topic "
                f"`{self.topic_name}`: session already exists!"
            )
        await self._signup_agent_users()

    async def _generate(self, query: str):
        result = None
        crunch("🧑 User:", query)

        # Send the query under the session
        async for event in self.runner.run(query):
            result_new = _custom_handle_adk_event(event)
            assert None in (result, result_new)
            result = result_new

        assert result is not None
        _display_result(result)

        await self.runner.update_session_state(
            {"generated_agents": result.model_dump(mode="json")}
        )

    async def _signup_agent_users(self):
        session = await self.runner.get_session()
        assert session is not None

        data = session.state["generated_agents"]
        result = AgentsCreationResult(**data)

        for agent_ins in result.result:
            username = agent_ins.username
            try:
                api.auth.signup_agent(agent_ins)
                crunch(
                    "✅ Agent created:",
                    "(:User {name:%s})-[:FOLLOWED]->(:Topic {name:%s})"
                    % (username, self.topic_name),
                )
            except HTTPException as e:
                assert e.status_code == 409
                crunch(f"⏭️ User {username} already exists!")
            finally:
                api.topics.follow_topic(self.topic_name, username)
