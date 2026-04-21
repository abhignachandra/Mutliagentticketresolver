"""Test the ClassifierAgent."""

import asyncio

from agents.classifier_agent import get_classifier_agent
from utility.llm_config import get_model_client


sample_tickets = [
    "The VPN is not connecting since morning.",
    "My laptop keyboard has stopped working.",
    "I forgot my domain password and cannot log in.",
    "Outlook keeps crashing whenever I open a meeting invite.",
    "Please grant me access to the finance SharePoint site.",
]


async def run_test():
    model_client = get_model_client()
    classifier = get_classifier_agent(model_client=model_client)
    try:
        for ticket in sample_tickets:
            print()
            print("Ticket:", ticket)
            result = await classifier.run(task=f"Classify this ticket: {ticket}")
            print("  ->", result.messages[-1].content)
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(run_test())
