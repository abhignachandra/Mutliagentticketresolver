# AgenticAIAbhigna — IT Ticket Classifier

A minimal AutoGen 0.4+ project that classifies IT support tickets into fixed categories (Network Issue, Hardware Issue, Software Bug, Access Request, Password Reset, Other) using an Azure OpenAI deployment.

## Layout

```
AgenticAIAbhigna/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── agenttest.py              # entry point / smoke test
├── agents/
│   ├── __init__.py
│   └── classifier_agent.py   # builds the AssistantAgent
└── utility/
    ├── __init__.py
    ├── llm_config.py         # builds the Azure OpenAI client
    └── prompt.py             # system prompt
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   # .\venv\Scripts\activate       # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```
   AZURE_OPENAI_DEPLOYMENT=gpt-4o
   AZURE_OPENAI_API_KEY=...
   AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

## Run

```bash
python agenttest.py
```

Expected output (per ticket):

```
🎟  Ticket: The VPN isn't connecting since morning.
   → {"ticket": "The VPN isn't connecting since morning.", "category": "Network Issue"}
```

## Notes

- This project uses the AutoGen 0.4+ API (`autogen-agentchat` + `autogen-ext`). The older `llm_config`/`pyautogen` style is not compatible with `autogen_agentchat.agents.AssistantAgent`.
- Keep `.env` out of git. A `.gitignore` entry is already provided.
