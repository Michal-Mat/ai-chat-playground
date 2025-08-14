"""
New Conversation Component.

Handles creating new conversations and displays usage statistics.
"""

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from conversations.manager import ConversationManager
    from integrations.openai.client import OpenAIClient
    from persistence.mongo_repository import ConversationRepository


class NewConversationComponent:
    """Component for creating new conversations and showing statistics."""

    @staticmethod
    def render(
        manager_class: type["ConversationManager"],
        client: "OpenAIClient",
        repository: "ConversationRepository",
    ) -> None:
        """
        Render the new conversation button and usage statistics.

        Args:
            manager_class: The ConversationManager class
            client: The OpenAI client
            repository: The conversation repository
        """
        st.header("Controls")

        if st.button("🆕 New Conversation", use_container_width=True):
            # Create new conversation manager
            new_manager: ConversationManager = manager_class(
                client=client,
                repository=repository,
            )
            st.session_state.manager = new_manager
            st.rerun()

        # Display usage statistics
        NewConversationComponent._render_statistics(repository)

    @staticmethod
    def _render_statistics(repository: "ConversationRepository") -> None:
        """
        Render usage statistics from MongoDB.

        Args:
            repository: The conversation repository
        """
        st.subheader("📊 Usage Statistics")

        try:
            stats = repository.get_statistics()

            # Create three columns for the statistics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="💬 Conversations",
                    value=f"{stats['total_conversations']:,}",
                )

            with col2:
                st.metric(
                    label="📨 Messages", value=f"{stats['total_messages']:,}"
                )

            with col3:
                st.metric(
                    label="🪙 Tokens", value=f"{stats['total_tokens']:,}"
                )

        except Exception as e:
            st.error(f"Error loading statistics: {e}")
            # Show zero stats as fallback
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="💬 Conversations", value="0")
            with col2:
                st.metric(label="📨 Messages", value="0")
            with col3:
                st.metric(label="🪙 Tokens", value="0")
