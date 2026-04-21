from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from utility.llm_config import get_model_client
from utility.prompt import classifier_prompt


def get_classifier_agent(model_client=None):
    client = model_client if model_client is not None else get_model_client()
    return AssistantAgent(
        name="ClassifierAgent",
        model_client=client,
        system_message=classifier_prompt,
    )
