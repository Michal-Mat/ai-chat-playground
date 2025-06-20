import os

import streamlit as st
from dotenv import load_dotenv

from integrations.openai.client import create_openai_client
from conversations.manager import ConversationManager
from conversations.types import Role  # noqa: E305

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

st.set_page_config(page_title="Hugging Chat", page_icon="🤖")

# -----------------------------------------------------------------------------
# Helper – get or create a ConversationManager tied to the user session
# -----------------------------------------------------------------------------


def _get_manager() -> ConversationManager:
    if "manager" not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY")
        # Organisation can also be passed through env var if needed
        client = create_openai_client(api_key=api_key)
        st.session_state.manager = ConversationManager(client)
    return st.session_state.manager


# -----------------------------------------------------------------------------
# Main UI
# -----------------------------------------------------------------------------

st.title("🤖 Hugging Chat Demo")

manager = _get_manager()

# Display existing messages
for message in manager.get_messages(include_system=False):
    chat_role = "assistant" if message.role == Role.ASSISTANT else "user"
    st.chat_message(chat_role).markdown(message.content)

# Input box – appears at the bottom of the chat
if prompt := st.chat_input("Type your message…"):
    # Show user prompt instantly
    st.chat_message("user").markdown(prompt)

    # Get AI response (blocking)
    with st.spinner("Thinking…"):
        answer = manager.chat(prompt)

    # Show assistant response
    st.chat_message("assistant").markdown(answer)

# -----------------------------------------------------------------------------
# Sidebar controls
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("Conversation")
    if st.button("💾 Save to MongoDB"):
        manager.save_to_repository()
        st.success("Conversation saved!")

    if st.button("🆕 New Conversation"):
        # Replace manager with a fresh conversation and refresh app
        manager = ConversationManager(manager.client)
        st.session_state.manager = manager
        st.experimental_rerun()