"""Knowledge base agent — retrieves IT solutions via Azure AI Search."""

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from utility.llm_config import get_model_client
from utility.guardrails import SAFETY_HEADER
from tools.knowledge_base_tool import search_similar_solution


KNOWLEDGE_BASE_PROMPT = SAFETY_HEADER + """
You are an IT support assistant that retrieves solutions to user issues.

When given an IT issue, call the `search_similar_solution` tool with a concise, keyword-rich
version of the issue. If the user message includes a category, pass it as the `category` argument.

After the tool returns, pick the single best match and reply with a short, actionable answer
that includes: the category, the recommended solution steps, and the matched problem for context.

If no match is relevant, say "No matching solution found; please escalate to a human agent."

Additional rules:
- Do NOT fabricate solutions. If the tool returns nothing relevant, say so.
- Do NOT invent commands that could delete data or disable security features.
- Do NOT call any tool other than `search_similar_solution`.
"""


def get_knowledge_base_agent(
    model_client: AzureOpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """Return a KnowledgeBaseAgent wired to Azure Search + Azure OpenAI."""
    client = model_client if model_client is not None else get_model_client()
    return AssistantAgent(
        name="KnowledgeBaseAgent",
        model_client=client,
        system_message=KNOWLEDGE_BASE_PROMPT,
        tools=[search_similar_solution],
        reflect_on_tool_use=True,
    )
