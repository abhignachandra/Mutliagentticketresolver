"""groupchat.py — 3-step team: Classifier -> KnowledgeBase -> Notification."""

import asyncio

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from agents.classifier_agent     import get_classifier_agent
from agents.knowledge_base_agent import get_knowledge_base_agent
from agents.notification_agent   import get_notification_agent
from utility.llm_config          import get_model_client

async def main():
    model_client = get_model_client()

    classifier = get_classifier_agent(model_client=model_client)
    kb_agent   = get_knowledge_base_agent(model_client=model_client)
    notifier   = get_notification_agent(model_client=model_client)

    # RoundRobin order: classifier -> kb_agent -> notifier.
    # TextMentionTermination("TERMINATE") lets the chat stop early when either
    # the KB resolves the ticket (and says TERMINATE) or the notifier finishes
    # escalating. max_turns=3 is a hard safety cap (one turn per agent).
    team = RoundRobinGroupChat(
        participants=[classifier, kb_agent, notifier],
        max_turns=3,
        termination_condition=TextMentionTermination("TERMINATE"),
    )

    task = (
        "IT ticket: Outlook crashes every time I open it.\n\n"
        "Classifier: categorize this issue.\n"
        "KnowledgeBaseAgent: search the knowledge base. If you find a confident "
        "solution, present it and end your message with TERMINATE on its own line. "
        "If you CANNOT resolve the issue, say so clearly and do NOT write TERMINATE.\n"
        "NotificationAgent: only speak if the knowledge base could not resolve the "
        "ticket. Call the escalate_ticket_with_email tool, then end with TERMINATE."
    )

    try:
        await Console(team.run_stream(task=task))
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())