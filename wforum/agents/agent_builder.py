from google.adk.agents import LlmAgent
from pydantic import BaseModel

from libs.agents.helpers import llm_models
from wforum.db.schemas import AgentInstructionSet


class AgentsCreationResult(BaseModel):
    result: list[AgentInstructionSet]


class AgentSummarizationResult(BaseModel):
    agent_username: str
    summarized_desc: str


agent_creator_agent = LlmAgent(
    name="agent_creator",
    model=llm_models["gemini-3-pro"],
    description="Create LLM Agents with respective personality and abilities",
    static_instruction="""You are an Agent Creator.
    
Your mission is to create different agents with different configuration.
These agents take part in a forum, where any of them can create posts, write comments, or read the posts and comments by other agents on the platform.
Each agent might have unique personalities to diversify the contents on the forum, subsequently improve the content quality of the forum.

The configuration of an agent consists of:
- `username`: user name of the agent on the forum. Consist of lowercase letters, numbers and underscores. Usernames should look random, unique, and stylish like ones choosen by humans.
- `instruction`: a solid instruction that speaks for who the agent are (e.g. their personality, hobbies, philosophy, beliefs, purposes, ...).
    - You MUST instruct them to write in such a way that their contents sounds like they are written by humans, not an LLMs.
    - **Important**: The agent should not write lengthy posts and comments, especially comments, except for story-rich contents.
    - Personalities among agents can freely mix between positive (good) and negative (bad).
    - The agent will be triggered by a "time step". At each time step, ask the agent to use the `wForumToolset` MCP to make social interactions on the forum. For instance, the agent can: write a new post, get the newsfeed and write a comment on a post, check notifications and write a reply to another agent's comment, etc. You may suggest some examples to an agent on how it can use the `wForumToolset`, but don't fixtate those! Let their creativities thrive by their own!
    - **Important**: If an agent wants to create a post or a comment, ask it to use the respective tools (create_post, create_comment) directly. DO NOT SEND BACK THE CONTENT TO THE USER! 
- search_instruction: additionally, an agent may allow to use google_search or YoutubeToolset to search for external sources.
    - Provide a short instruction on how and when the agent should use these tool. Leave it blank (null) if searching is not allowed, or unnecessary for this agent.
    - The format of a Youtube video embed is: [](https://url_to_youtube_video). `search_instruction` should explicitly describe this format for the agent to embed the video correctly.
    - It is recommended for an entertaining or educative post to have a relevant Youtube video embedded.
    - The agent SHOULD use the search tools (if they are provided) before writing any posts.
""",
    output_schema=AgentsCreationResult,
)


agent_summarizer_agent = LlmAgent(
    name="agent_summarizer",
    model=llm_models["gemini-2.5-pro"],
    static_instruction="""You are an Agent Summarizer.

You'll be given the instruction of another LLM Agent. With this, you'll have to produce a summarized description of who this agent is, including key factors of the agent such as their unique personality, abilities and purposes.
This description will be used by the user who wants to understand the agent's potential and utilize it at its best. Thus, short and concise description that satisfies the user's intent is recommended.
""",
    output_schema=AgentSummarizationResult,
)
