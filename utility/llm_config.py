import os
from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

load_dotenv()


def _required(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {var_name}. "
            f"Add it to your .env file (see .env.example)."
        )
    return value


def get_model_client() -> AzureOpenAIChatCompletionClient:
    """Build and return a configured Azure OpenAI chat-completion client."""
    # `azure_deployment` = the deployment name in Azure (e.g. "gpt-4o").
    # `model`            = the underlying model id used for token accounting.
    #                      Defaults to the deployment name, but can be pinned
    #                      (e.g. "gpt-4o-2024-11-20") to silence the version
    #                      mismatch warning.
    deployment = _required("AZURE_OPENAI_DEPLOYMENT")
    model = os.getenv("AZURE_OPENAI_MODEL", deployment)

    return AzureOpenAIChatCompletionClient(
        azure_deployment=deployment,
        model=model,
        api_version=_required("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=_required("AZURE_OPENAI_ENDPOINT"),
        api_key=_required("AZURE_OPENAI_API_KEY"),
        temperature=0,
    )
