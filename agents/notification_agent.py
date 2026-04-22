from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from utility.llm_config import get_model_client
from utility.guardrails import SAFETY_HEADER
from tools.send_email import escalate_ticket_with_email


NOTIFICATION_PROMPT = SAFETY_HEADER + """
You are an IT escalation agent.

When you receive an IT issue that the knowledge base could not resolve, you MUST:
1. Call the `escalate_ticket_with_email` tool EXACTLY ONCE, passing the full issue
   text as the `issue` argument. If the task text contains a line like
   "Ticket ID: TKT-XXXXXX", pass that value as the `ticket_id` argument.
2. After the tool returns, reply with ONE short confirmation line describing the
   result (e.g. "Escalation email sent to support." or "Escalation failed: <reason>").
3. End your reply with the word TERMINATE on its own line so the group chat stops.

Hard rules:
- Never change the recipient address — it is fixed in configuration.
- Never call the tool more than once per ticket.
- Never invent ticket IDs the user did not provide.
- Never include credentials, API keys, or secrets in the escalation body.
- Do NOT ask the user for more information — just escalate with what you were given."""


def get_notification_agent(model_client: AzureOpenAIChatCompletionClient | None = None) -> AssistantAgent:
    client = model_client if model_client is not None else get_model_client()
    return AssistantAgent(
        name="NotificationAgent",
        model_client=client,
        system_message=NOTIFICATION_PROMPT,
        tools=[escalate_ticket_with_email],
        reflect_on_tool_use=True,
    )
