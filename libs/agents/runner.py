import uuid

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from google.genai import types

from .helpers import handle_adk_event


class CustomAgentRunner:
    def __init__(
        self,
        *,
        agent: LlmAgent,
        user_id: str = "default",
        session_id: str | None = None,
        sqlite_uri: str = "data/temp.db",
        compaction_config: EventsCompactionConfig | None = None,
    ):
        """
        Initialize an Agent Runner with customizable:
        - `user_id`: a string, default to `"default"`
        - `session_id`: a string, default to a random `uuid4` hex
        - `events_compaction_config`: compaction config, default to `None`

        `app_name` is be set to `"default"` for all runners.
        """

        self.agent = agent
        self.session_service = SqliteSessionService(sqlite_uri)

        self.user_id = user_id
        self.app_name = "default"
        self.session_id = session_id or uuid.uuid4().hex[:12]

        self.app = App(
            name=self.app_name,
            root_agent=self.agent,
            events_compaction_config=compaction_config,
        )

    async def get_session(self):
        return await self.session_service.get_session(
            user_id=self.user_id, app_name=self.app.name, session_id=self.session_id
        )

    async def create_session(self):
        if (session := await self.get_session()) is not None:
            return session
        return await self.session_service.create_session(
            user_id=self.user_id, app_name=self.app.name, session_id=self.session_id
        )

    async def run(self, query: str | types.Content):
        await self.create_session()
        if isinstance(query, str):
            query = types.Content(role="user", parts=[types.Part(text=query)])

        runner = Runner(app=self.app, session_service=self.session_service)

        async for event in runner.run_async(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=query,
        ):
            yield event

    async def send_query(self, query: str | types.Content):
        result: list[str] = []

        async for event in self.run(query):
            data = handle_adk_event(event)
            result.extend(data.text)

        return "\n\n".join(result)

    async def get_session_state(self, key: str, default=None):
        session = await self.create_session()
        return session.state.get(key, default)

    async def update_session_state(self, state_delta: dict[str, object]):
        event = Event(
            author="user",
            actions=EventActions(state_delta=state_delta),
        )
        await self.session_service.append_event(await self.create_session(), event)
