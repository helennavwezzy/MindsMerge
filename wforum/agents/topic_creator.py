from google.adk.agents import LlmAgent
from pydantic import BaseModel

from libs.agents.helpers import llm_models


class TopicCreationResult(BaseModel):
    topic_name: str
    description: str


topic_creator_agent = LlmAgent(
    name="topic_creator",
    model=llm_models["gemini-2.5-pro"],
    static_instruction="""You are an Topic Creator.

The user is the maintainer of a new forum website.
In order to test the functionality of the topic feature (similar to Reddit communities).
Your mission is to determine the field of topic according to the description in the query of the user and suggest the corresponding:
- topic_name: a single representative name for the topic. Consists of lowercase and uppercase letters and numbers only. For example: "Valorant", "Piano", "UnrealEngine".
- description: a brief introduction that speaks for what this topic is, what the posts of this topic on the forum are about. Make it catchy, mischievous and show its sense of humour!
""",
    output_schema=TopicCreationResult,
)
