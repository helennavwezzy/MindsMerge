from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import google_search as search_tool

from libs.agents.helpers import llm_models

google_search = LlmAgent(
    name="google_search",
    model=llm_models["gemini-2.5-flash"],
    instruction="""You are a specialist in Google Search. Your mission is to:
- receive the user query.
- use the `google_search` tool to send that exact query.
- after the search completes, send the exact result back to the user.
    """,
    tools=[search_tool],
)
