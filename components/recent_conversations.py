"""
Recent Conversations Component.

Displays a list of recent conversations with load functionality.
"""

from typing import TYPE_CHECKING

import streamlit as st

from conversations.types import Role

if TYPE_CHECKING:
    from conversations.manager import ConversationManager


class RecentConversationsComponent:
    """Component for displaying and managing recent conversations."""

    @staticmethod
    def render(
        manager: "ConversationManager", max_conversations: int = 10
    ) -> None:
        """
        Render the recent conversations section.

        Args:
            manager: The current conversation manager
            max_conversations: Maximum number of conversations to display
        """
        st.subheader("📋 Recent Conversations")

        try:
            recent_conversations = manager.repository.list(
                limit=max_conversations
            )

            if recent_conversations:
                for conv in recent_conversations:
                    RecentConversationsComponent._render_conversation_item(
                        conv, manager
                    )
            else:
                st.write("No recent conversations")

        except Exception as e:
            st.error(f"Error loading conversations: {e}")

    @staticmethod
    def _render_conversation_item(
        conversation, manager: "ConversationManager"
    ) -> None:
        """
        Render a single conversation item.

        Args:
            conversation: The conversation object to render
            manager: The current conversation manager
        """
        # Create a short title for display
        display_title = RecentConversationsComponent._get_display_title(
            conversation
        )

        # Show conversation with neat layout
        if st.button(
            f"💬 {display_title}",
            key=f"load_{conversation.metadata.id}",
            use_container_width=True,
        ):
            # Load the selected conversation
            loaded_manager = manager.__class__.load_from_repository(
                client=manager.client,
                conversation_id=conversation.metadata.id,
                repository=manager.repository,
            )
            st.session_state.manager = loaded_manager
            st.rerun()

        # Show stats in a neat row below the button
        RecentConversationsComponent._render_conversation_stats(conversation)

        # Add small spacing between conversations
        st.write("")

    @staticmethod
    def _get_display_title(conversation) -> str:
        """
        Get a display-friendly title for the conversation.

        Args:
            conversation: The conversation object

        Returns:
            A formatted display title
        """
        if conversation.metadata.title:
            return (
                conversation.metadata.title[:30] + "..."
                if len(conversation.metadata.title) > 30
                else conversation.metadata.title
            )
        else:
            # Use first user message as title
            first_user_msg = next(
                (
                    msg.content
                    for msg in conversation.messages
                    if msg.role == Role.USER
                ),
                "Untitled",
            )
            return (
                first_user_msg[:30] + "..."
                if len(first_user_msg) > 30
                else first_user_msg
            )

    @staticmethod
    def _render_conversation_stats(conversation) -> None:
        """
        Render conversation statistics.

        Args:
            conversation: The conversation object
        """
        stats_col1, stats_col2 = st.columns(2)

        with stats_col1:
            st.caption(f"📨 {conversation.metadata.message_count} messages")

        with stats_col2:
            if conversation.metadata.total_tokens > 0:
                st.caption(f"🪙 {conversation.metadata.total_tokens} tokens")
            else:
                st.caption("🪙 0 tokens")
