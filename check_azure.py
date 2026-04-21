import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

load_dotenv()

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_key    = os.getenv("AZURE_OPENAI_API_KEY")
endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT")
api_ver    = os.getenv("AZURE_OPENAI_API_VERSION")

print("--- Loaded env values ---")
print(f"DEPLOYMENT : {deployment!r}")
print(f"ENDPOINT   : {endpoint!r}")
print(f"API_VERSION: {api_ver!r}")
print(f"API_KEY    : len={len(api_key) if api_key else 0}, "
      f"starts={api_key[:4] if api_key else ''}..., "
      f"ends=...{api_key[-4:] if api_key else ''}")
print()

async def main():
    client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_ver,
    )
    resp = await client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Say hi in 3 words."}],
        max_tokens=20,
    )
    print("--- Response ---")
    print(resp.choices[0].message.content)
    await client.close()

asyncio.run(main())
