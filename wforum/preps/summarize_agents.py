import json
from typing import cast

from google.adk.events import Event

from libs.agents import CustomAgentRunner
from libs.agents.helpers import crunch, handle_adk_event
from wforum.db import api, schemas
from wforum.db.models import User

from ..agents import AgentSummarizationResult, agent_summarizer_agent


def _custom_handle_adk_event(event: Event):
    if event.is_final_response():
        assert event.content is not None
        assert event.content.parts
        text = event.content.parts[0].text
        assert text is not None
        return AgentSummarizationResult(**json.loads(text))
    else:
        handle_adk_event(event)


def _show_summary_result(result: AgentSummarizationResult):
    crunch(
        f"📜 Summarized description of agent `{result.agent_username}`:",
        result.summarized_desc,
    )


class SummarizeAgentsPrep:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.runner = CustomAgentRunner(
            sqlite_uri="data/prep_data.db",
            agent=agent_summarizer_agent,
            user_id="summarize_agents_prep",
            session_id=topic_name,
        )
        self.result: AgentSummarizationResult

    async def run(self):
        await self._generate()

        await self._merge_saved_summaries()

    async def _generate(self):
        result = cast(
            list[dict], await self.runner.get_session_state("agent_summaries", [])
        )

        for agent in api.topics.get_topic_followers(self.topic_name):
            if any(r["user"]["name"] == agent.name for r in result):
                continue

            # Define user query
            query = f"Original instruction of agent `{agent.name}`:\n```\n{agent.instruction}\n```"

            crunch("🧑 User:", query)

            summary = None

            # Send the query under the session
            async for event in self.runner.run(query):
                summary_new = _custom_handle_adk_event(event)
                assert None in (summary, summary_new)
                summary = summary_new

            assert summary is not None
            assert summary.agent_username == agent.name

            result.append(
                {"user": agent.dump(), "summarized_desc": summary.summarized_desc}
            )

            _show_summary_result(summary)

        # Update session state from result
        await self.runner.update_session_state(
            {"agent_summaries": result},
        )

    async def _merge_saved_summaries(self):
        session = await self.runner.get_session()
        assert session is not None

        result = session.state["agent_summaries"]

        for r in result:
            api.users.patch_user(
                schemas.UserPatchRequest(bio=r["summarized_desc"]), User(**r["user"])
            )

            crunch(f"✅ Summarized description set for agent {r['user']['name']}!")
