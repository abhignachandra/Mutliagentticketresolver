"""Streamlit UI for the SupportX AI Assist pipeline (AutoGen 0.4+)."""

import asyncio
import random
import string
from pathlib import Path

import streamlit as st

from autogen_agentchat.teams import RoundRobinGroupChat

from agents.classifier_agent import get_classifier_agent
from agents.knowledge_base_agent import get_knowledge_base_agent
from agents.notification_agent import get_notification_agent
from utility.llm_config import get_model_client


# ---------- helpers ----------
def generate_ticket_id(prefix: str = "TKT", length: int = 6) -> str:
    """Generate a random alphanumeric ticket ID like TKT-4F9AZX."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}-{suffix}"


def _last_text_from(result, source_name: str) -> str:
    """Pick the last message authored by `source_name` from a team/agent run result."""
    for msg in reversed(result.messages):
        if getattr(msg, "source", "") == source_name:
            content = msg.content
            return content if isinstance(content, str) else str(content)
    # fallback: just return the last message content
    last = result.messages[-1]
    return last.content if isinstance(last.content, str) else str(last.content)


# ---------- agent runs ----------
async def run_resolution_pipeline(user_issue: str) -> str:
    """Classifier -> KnowledgeBaseAgent. Returns the KB agent's final reply."""
    model_client = get_model_client()
    try:
        classifier = get_classifier_agent(model_client=model_client)
        kb_agent = get_knowledge_base_agent(model_client=model_client)
        team = RoundRobinGroupChat(
            participants=[classifier, kb_agent],
            max_turns=2,
        )
        result = await team.run(task=user_issue)
        return _last_text_from(result, "KnowledgeBaseAgent")
    finally:
        await model_client.close()


async def run_escalation(issue_text: str) -> str:
    """Run NotificationAgent standalone to email support."""
    model_client = get_model_client()
    try:
        notifier = get_notification_agent(model_client=model_client)
        result = await notifier.run(task=issue_text)
        return _last_text_from(result, "NotificationAgent")
    finally:
        await model_client.close()


# ---------- Streamlit UI ----------
st.set_page_config(page_title="SupportX AI Assist", page_icon="🤖", layout="centered")

# Load custom CSS if it exists (don't crash if it doesn't).
css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="title-container">
        <h1>🤖 SupportX AI Assist</h1>
    </div>
    <div class="subtitle">Your Personalized AI IT Support Assistant</div>
    <div class="description"><em>Facing a tech issue? Describe it below and let SupportX AI Assist handle it for you.</em></div>
    """,
    unsafe_allow_html=True,
)

# Session state setup
for key, default in [
    ("final_response", None),
    ("user_input", ""),
    ("awaiting_feedback", False),
    ("feedback_given", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Input
st.markdown(
    '<div class="input-label">💬 <strong>Describe your IT issue:</strong></div>',
    unsafe_allow_html=True,
)
user_input = st.text_area(
    "Your issue",
    value=st.session_state.user_input,
    height=150,
    label_visibility="collapsed",
)

# Resolve
if st.button("🚀 Resolve Now") and user_input.strip():
    with st.spinner("SupportX AI Assist is resolving your issue..."):
        st.session_state.user_input = user_input
        try:
            final = asyncio.run(run_resolution_pipeline(user_input))
            st.session_state.final_response = final
            st.session_state.awaiting_feedback = True
            st.session_state.feedback_given = False
            st.success("✅ **AI Response:**")
            st.markdown(final)
        except Exception as e:
            st.error(f"Something went wrong while resolving: {e}")

# Feedback
if (
    st.session_state.awaiting_feedback
    and st.session_state.final_response
    and not st.session_state.feedback_given
):
    st.markdown("### 🙋 Was this solution helpful?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, issue resolved"):
            st.session_state.feedback_given = True
            st.session_state.awaiting_feedback = False
            st.success("🎉 Great! We're glad your issue is resolved. Thank you!")

    with col2:
        if st.button("❌ No, not helpful"):
            st.session_state.feedback_given = True
            st.session_state.awaiting_feedback = False
            ticket_id = generate_ticket_id()
            st.warning(
                f"⚠️ We're escalating this issue to IT support.\n\n"
                f"📄 **Ticket Created: `{ticket_id}`**"
            )
            escalation_msg = (
                "Unresolved IT Issue\n\n"
                f"User reported: \"{st.session_state.user_input}\"\n"
                f"Ticket ID: {ticket_id}"
            )
            try:
                reply = asyncio.run(run_escalation(escalation_msg))
                st.info(f"📨 **Notification Agent Response:**\n\n{reply}")
            except Exception as e:
                st.error(f"Escalation error: {e}")
