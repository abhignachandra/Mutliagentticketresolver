import os
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

AZURE_SEARCH_ENDPOINT   = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY        = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX_NAME = "it-ticket-solutions-index"

AZURE_OPENAI_API_KEY     = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT    = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

EMBED_DEPLOYMENT   = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or AZURE_OPENAI_DEPLOYMENT
SEARCH_API_VERSION = "2024-07-01"

openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)


def embed_text(text: str):
    response = openai_client.embeddings.create(input=[text], model=EMBED_DEPLOYMENT)
    return response.data[0].embedding


def search_similar_solution(query: str, category: str | None = None, top_k: int = 3) -> str:
    embedding = embed_text(query)
    url = (
        f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX_NAME}"
        f"/docs/search?api-version={SEARCH_API_VERSION}"
    )
    headers = {"Content-Type": "application/json", "api-key": AZURE_SEARCH_KEY}
    payload = {
        "search": query,
        "vectorQueries": [{
            "kind": "vector",
            "vector": embedding,
            "fields": "embedding",
            "k": top_k,
        }],
        "select": "id,category,problem,solution",
        "top": top_k,
    }
    if category:
        safe = category.replace("'", "''")
        payload["filter"] = "category eq '" + safe + "'"

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return f"Error while searching: {response.text}"

    results = response.json().get("value", [])
    if not results:
        return "No matching solutions found."

    lines = []
    for idx, doc in enumerate(results, 1):
        lines.append(
            f"Result {idx}:\n"
            f"  Category: {doc.get('category')}\n"
            f"  Problem:  {doc.get('problem')}\n"
            f"  Solution: {doc.get('solution')}"
        )
    return "\n\n".join(lines)


if __name__ == "__main__":
    print(search_similar_solution("My Outlook crashes every time I open it", category="Software Bug"))
