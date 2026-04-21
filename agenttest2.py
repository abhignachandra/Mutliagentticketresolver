"""Test the KnowledgeBaseAgent end-to-end."""

import asyncio

from agents.knowledge_base_agent import get_knowledge_base_agent
from utility.llm_config import get_model_client


sample_tickets = [
    ("The VPN is not connecting since morning.",     "Network Issue"),
    ("My Outlook crashes every time I open it.",     "Software Bug"),
    ("I forgot my email password.",                  "Password Reset"),
]


async def run_kb_test():
    model_client = get_model_client()
    kb_agent = get_knowledge_base_agent(model_client=model_client)
    try:
        for ticket, category in sample_tickets:
            print()
            print("🎟  Ticket:       ", ticket)
            print("    Category hint:", category)
            task = f"Find the fix for this issue: {ticket} Category is {category}."
            result = await kb_agent.run(task=task)
            print("   →", result.messages[-1].content)
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(run_kb_test())
