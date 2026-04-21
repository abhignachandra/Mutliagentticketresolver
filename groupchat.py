"""groupchat.py — deterministic 2-step team: Classifier -> KnowledgeBase."""

import asyncio

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from agents.classifier_agent     import get_classifier_agent
from agents.knowledge_base_agent import get_knowledge_base_agent
from utility.llm_config          import get_model_client


async def main():
    model_client = get_model_client()

    classifier = get_classifier_agent(model_client=model_client)
    kb_agent   = get_knowledge_base_agent(model_client=model_client)

    # RoundRobin: classifier speaks on turn 1, kb_agent on turn 2, then stops.
    team = RoundRobinGroupChat(
        participants=[classifier, kb_agent],
        max_turns=2,
    )

    task = "Please resolve this issue: Outlook crashes every time I open it."

    try:
        await Console(team.run_stream(task=task))
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
