from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from utility.llm_config import get_model_client
from tools.send_email import escalate_ticket_with_email


NOTIFICATION_PROMPT = """You are an IT escalation agent.

When you receive an IT issue that the knowledge base could not resolve, you MUST:
1. Call the `escalate_ticket_with_email` tool exactly once, passing the full issue text
   as the `issue` argument.
2. After the tool returns, reply with ONE short confirmation line describing the
   result (e.g. "Escalation email sent to support." or "Escalation failed: <reason>").
3. End your reply with the word TERMINATE on its own line so the group chat stops.

Do not invent ticket IDs. Do not call the tool more than once. Do not ask the user
for more information — just escalate with whatever issue text you were given."""


def get_notification_agent(model_client: AzureOpenAIChatCompletionClient | None = None) -> AssistantAgent:
    client = model_client if model_client is not None else get_model_client()
    return AssistantAgent(
        name="NotificationAgent",
        model_client=client,
        system_message=NOTIFICATION_PROMPT,
        tools=[escalate_ticket_with_email],
        reflect_on_tool_use=True,
    )
