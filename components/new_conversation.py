"""
New Conversation Component.

Handles creating new conversations.
"""

import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from conversations.manager import ConversationManager


class NewConversationComponent:
    """Component for creating new conversations."""

    @staticmethod
    def render(manager_class, client, repository) -> None:
        """
        Render the new conversation button.

        Args:
            manager_class: The ConversationManager class
            client: The OpenAI client
            repository: The conversation repository
        """
        if st.button("🆕 New Conversation", use_container_width=True):
            # Create new conversation manager
            new_manager = manager_class.from_client(
                client=client,
                repository=repository,
            )
            st.session_state.manager = new_manager
            st.rerun()
