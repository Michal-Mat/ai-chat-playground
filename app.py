import streamlit as st  # type: ignore
from dotenv import load_dotenv

import core.bootstrap  # noqa: F401

# Import our UI components
from components import (
    ChatInputComponent,
    MessageDisplayComponent,
    NewConversationComponent,
    RecentConversationsComponent,
    SidebarSettingsComponent,
    SystemPromptEditorComponent,
)

# Import the bootstrap to setup DI
from conversations.manager import ConversationManager
from core.container import get_service

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

st.set_page_config(page_title="Open AI Chat", page_icon="🤖")


# -----------------------------------------------------------------------------
# Helper – get or create a ConversationManager using DI
# -----------------------------------------------------------------------------


def _get_manager() -> ConversationManager:
    """Get ConversationManager from DI container."""
    if "manager" not in st.session_state:
        # Get a new instance from the container (factory pattern)
        st.session_state.manager = get_service("conversation_manager")
    return st.session_state.manager


# -----------------------------------------------------------------------------
# Main UI
# -----------------------------------------------------------------------------

st.title("🤖 AI Chat Demo")

manager = _get_manager()

# Sidebar controls
with st.sidebar:
    # Settings component
    manager: ConversationManager = SidebarSettingsComponent.render(manager)

    st.divider()

    # New conversation component
    manager_class = manager.__class__
    NewConversationComponent.render(
        manager_class=manager_class,
        client=manager.client,
        repository=manager.repository,
    )

    st.divider()

    # Recent conversations component
    RecentConversationsComponent.render(manager, max_conversations=10)

    st.divider()

    # System prompt editor component
    manager = SystemPromptEditorComponent.render(manager)

    st.divider()


# Show active model caption after potential update
st.caption(f"Model in use: **{manager.conversation.settings.model}**")

# Message display component
messages = manager.get_messages(include_system=True)
MessageDisplayComponent.render_messages(messages)

# Chat input component
manager = ChatInputComponent.render(manager)
