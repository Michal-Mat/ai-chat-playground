import os

import streamlit as st  # type: ignore
from dotenv import load_dotenv

from integrations.openai.client import create_openai_client
from conversations.manager import ConversationManager
from conversations.types import Role, ChatModel  # noqa: E305

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

# Sidebar controls (placed early to allow caption to reflect selection)
with st.sidebar:
    st.header("Settings")
    model_options = [m.value for m in ChatModel]
    default_index = (
        model_options.index(manager.conversation.settings.model)
        if manager.conversation.settings.model in model_options
        else 0
    )
    selected_model = st.selectbox(
        "OpenAI model",
        options=model_options,
        index=default_index,
    )

    # Update manager if model selection changed
    if selected_model != manager.conversation.settings.model:
        manager.update_settings(model=selected_model)
        st.rerun()

    st.divider()
    if st.button("💾 Save conversation to MongoDB"):
        manager.save_to_repository()
        st.success("Conversation saved!")

    if st.button("🆕 New Conversation"):
        manager = ConversationManager(manager.client)
        st.session_state.manager = manager
        st.rerun()

# Show active model caption after potential update
st.caption(f"Model in use: **{manager.conversation.settings.model}**")

# Display existing messages
for message in manager.get_messages(include_system=False):
    chat_role = "assistant" if message.role == Role.ASSISTANT else "user"
    if chat_role == "assistant":
        model_label = getattr(
            message,
            "model",
            manager.conversation.settings.model,
        )
        content = f"*_{model_label}_*\n\n{message.content}"
    else:
        content = message.content
    st.chat_message(chat_role).markdown(content)

# Input box – appears at the bottom of the chat
if prompt := st.chat_input("Type your message…"):
    # Show user prompt instantly
    st.chat_message("user").markdown(prompt)

    # Get AI response (blocking)
    with st.spinner("Thinking…"):
        try:
            answer = manager.chat(prompt)
            last_msg = manager.get_messages()[-1]
            model_label_resp = getattr(
                last_msg,
                "model",
                manager.conversation.settings.model,
            )
            st.chat_message("assistant").markdown(
                f"*_{model_label_resp}_*\n\n{answer}"
            )
        except Exception as exc:
            error_text = (
                f"⚠️ **Error calling OpenAI:** {exc}\n\n"
                "Please revise your prompt or choose a different model and "
                "try again."
            )
            st.chat_message("assistant").markdown(error_text)