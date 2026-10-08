from google.adk.agents import LlmAgent
from google.adk.agents.llm_agent import ToolUnion
from google.adk.apps.app import EventsCompactionConfig
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_api_tool import YoutubeToolset
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPServerParams,
)
from google.genai import types

import envy
from libs.agents import (
    CustomAgentRunner,
    LongRunningRequestType,
    crunch,
    get_auth_config,
    handle_adk_event,
    llm_models,
    make_func_response,
)
from libs.jwt_auth import create_access_token
from wforum.db.models import Topic, User
from wforum.tools import google_search


class ContentCreatorRunner(CustomAgentRunner):
    def __init__(self, *, topic: Topic, agent_user: User):
        self.topic = topic
        assert agent_user.instruction is not None

        self.access_token: str | None = None
        tools = self.get_agent_tools(agent_user)

        agent = LlmAgent(
            name=agent_user.name,
            model=llm_models["gemini-3-pro"],
            static_instruction=agent_user.instruction,
            tools=tools,
        )

        compaction_config = EventsCompactionConfig(
            overlap_size=4,
            compaction_interval=7,
        )

        super().__init__(
            sqlite_uri="data/main_data.db",
            agent=agent,
            user_id=agent.name,
            session_id=topic.name,
            compaction_config=compaction_config,
        )

    async def get_time_step(self):
        if await self.get_session_state("time_step") is None:
            await self.update_session_state({"time_step": 0})
        return await self.get_session_state("time_step")

    def get_agent_tools(self, agent_user: User):
        # Any agent must have instruction
        assert agent_user.instruction is not None

        self.access_token = self.access_token or create_access_token(agent_user.name)

        wForumToolset = McpToolset(
            connection_params=StreamableHTTPServerParams(
                url=envy.WFORUM_MCP_URL,
                timeout=15,
                headers={"Authorization": f"Bearer {self.access_token}"},
            ),
        )

        tools: list[ToolUnion] = [wForumToolset]
        if "google" in agent_user.instruction.lower():
            tools.append(AgentTool(google_search))

        if "youtube" in agent_user.instruction.lower():
            tools.append(
                YoutubeToolset(
                    envy.GOOGLE_OAUTH_CLIENT_ID, envy.GOOGLE_OAUTH_CLIENT_SECRET
                )
            )

        return tools

    async def send_query(self, query: str | types.Content):
        result: list[str] = []
        need_approval = None

        async for event in self.run(query):
            data = handle_adk_event(event)
            result.extend(data.text)

            need_approval = data.request
            if need_approval:
                break
        else:
            return "\n\n".join(result)

        for req, func_call in need_approval:
            crunch(
                "-------------------------------------------------",
                "⚠️ Authentication required by agent.",
                f"Function name: {req}\t(ID: {func_call.id})",
                "Arguments:",
                func_call.args,
                "-------------------------------------------------",
            )

            assert func_call.id is not None
            assert req == LongRunningRequestType.CRED

            result.append(await self.handle_cred_req(func_call))

        return "\n\n".join(result)

    async def handle_cred_req(self, func_call: types.FunctionCall):
        # Doc: https://google.github.io/adk-docs/tools-custom/authentication/#2-handling-the-interactive-oauthoidc-flow-client-side

        auth_config = get_auth_config(func_call)

        auth_cred = auth_config.exchanged_auth_credential
        assert auth_cred is not None
        assert auth_cred.oauth2 is not None
        assert auth_cred.oauth2.auth_uri is not None

        base_auth_url = auth_cred.oauth2.auth_uri
        # TODO (glowo): this is hard-coded
        redirect_uri = "http://localhost:8000/callback"
        auth_request_uri = f"{base_auth_url}&redirect_uri={redirect_uri}"

        print("Open in browser:")
        print(auth_request_uri, end="\n\n")
        auth_response_uri = input("Input your callback URL: ").strip()

        auth_cred.oauth2.redirect_uri = redirect_uri
        auth_cred.oauth2.auth_response_uri = auth_response_uri

        # Construct the FunctionResponse Content object
        auth_response_content = make_func_response(
            func_call=func_call, response=auth_config.model_dump()
        )

        print("\nSubmitting authentication details back to the agent...")
        return await self.send_query(auth_response_content)

    async def step(self):
        time_step = await self.get_time_step()
        assert isinstance(time_step, int)

        time_step += 1
        query = f"Current time step: {time_step}"
        crunch("🧑 User:", query)

        result = await self.send_query(query)
        await self.update_session_state({"time_step": time_step})

        return result
