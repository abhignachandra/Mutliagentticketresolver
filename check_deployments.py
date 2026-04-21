import os, asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

load_dotenv()

chat_deploy  = os.getenv("AZURE_OPENAI_DEPLOYMENT")
embed_deploy = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

print(f"AZURE_OPENAI_DEPLOYMENT            = {chat_deploy!r}")
print(f"AZURE_OPENAI_EMBEDDING_DEPLOYMENT  = {embed_deploy!r}")
print()

async def main():
    client = AsyncAzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key        = os.getenv("AZURE_OPENAI_API_KEY"),
        api_version    = os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    for label, deploy in [("chat", chat_deploy), ("embed", embed_deploy or chat_deploy)]:
        if not deploy:
            continue
        # try chat
        try:
            r = await client.chat.completions.create(
                model=deploy,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5,
            )
            print(f"[{label}] {deploy!r}: supports CHAT -> {r.choices[0].message.content.strip()!r}")
        except Exception as e:
            print(f"[{label}] {deploy!r}: CHAT not supported ({type(e).__name__})")
        # try embed
        try:
            r = await client.embeddings.create(model=deploy, input=["hi"])
            print(f"[{label}] {deploy!r}: supports EMBED -> dim={len(r.data[0].embedding)}")
        except Exception as e:
            print(f"[{label}] {deploy!r}: EMBED not supported ({type(e).__name__})")
    await client.close()

asyncio.run(main())
