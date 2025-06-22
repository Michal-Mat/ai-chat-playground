import streamlit as st  # type: ignore
from dotenv import load_dotenv

# Import the bootstrap to setup DI
import core.bootstrap  # noqa: F401
from core.container import get_service
from conversations.types import Role, ChatModel, Persona

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

st.set_page_config(page_title="Open AI Chat", page_icon="🤖")


# -----------------------------------------------------------------------------
# Helper – get or create a ConversationManager using DI
# -----------------------------------------------------------------------------


def _get_manager():
    """Get ConversationManager from DI container."""
    if "manager" not in st.session_state:
        # Get a new instance from the container (factory pattern)
        st.session_state.manager = get_service('conversation_manager')
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
    persona_options = ["None"] + [p.value for p in Persona]
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

    selected_persona = st.selectbox(
        "Assistant persona",
        options=persona_options,
        index=(
            persona_options.index(manager.conversation.settings.persona.value)
            if manager.conversation.settings.persona
            else 0
        ),
    )

    if (selected_persona == "None"):
        persona_obj = None
    else:
        persona_obj = Persona(selected_persona)

    if persona_obj != manager.conversation.settings.persona:
        manager.update_settings(persona=persona_obj)
        st.rerun()

    if selected_model != manager.conversation.settings.model:
        manager.update_settings(model=selected_model)
        st.rerun()

    # Toggle – enable/disable reasoning feature
    reasoning_enabled = st.checkbox(
        "🧠 Enable multi-step reasoning",
        value=manager.conversation.settings.reasoning,
    )

    if reasoning_enabled != manager.conversation.settings.reasoning:
        manager.update_settings(reasoning=reasoning_enabled)
        st.rerun()

    st.divider()
    if st.button("💾 Save conversation to MongoDB"):
        manager.save_to_repository()
        st.success("Conversation saved!")

    if st.button("🆕 New Conversation"):
        # Get a new manager instance from DI container
        manager = get_service('conversation_manager')
        st.session_state.manager = manager
        st.rerun()

    # --- System prompt editor ---
    sys_msg = manager.conversation.get_system_message()
    current_sys_prompt = sys_msg.content if sys_msg else ""

    st.caption(f"_Current prompt:_ {current_sys_prompt or '—'}")

    new_sys_prompt = st.text_area(
        "Edit system prompt (leave blank to keep current)",
        value="",
        placeholder=current_sys_prompt,
        height=100,
    )

    if st.button("Update system prompt") and new_sys_prompt.strip():
        manager.set_system_prompt(new_sys_prompt.strip())
        st.rerun()

    st.divider()

# Show active model caption after potential update
st.caption(f"Model in use: **{manager.conversation.settings.model}**")

# Display existing messages (include system prompt if present)
for message in manager.get_messages(include_system=True):
    chat_role = "assistant" if message.role == Role.ASSISTANT else "user"
    if message.role == Role.SYSTEM:
        st.chat_message(
            "assistant",
        ).markdown(
            f"🎯 _System prompt:_ {message.content}"
        )
        continue
    if chat_role == "assistant":
        model_label = getattr(
            message,
            "model",
            manager.conversation.settings.model,
        )
        persona_label = getattr(message, "persona", None)
        tag = model_label
        if persona_label:
            tag += f" · {persona_label}"
        content = f"*_{tag}_*\n\n{message.content}"
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
            persona_resp = getattr(last_msg, "persona", None)
            tag_resp = model_label_resp
            if persona_resp:
                tag_resp += f" · {persona_resp}"
            st.chat_message("assistant").markdown(
                f"*_{tag_resp}_*\n\n{answer}"
            )
        except Exception as exc:
            error_text = (
                f"⚠️ **Error calling OpenAI:** {exc}\n\n"
                "Please revise your prompt or choose a different model and "
                "try again."
            )
            st.chat_message("assistant").markdown(error_text)
