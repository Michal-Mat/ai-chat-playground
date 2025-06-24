"""
System Prompt Editor Component.

Allows users to view and edit the system prompt.
"""

import streamlit as st
from typing import TYPE_CHECKING
from conversations.models import Message

if TYPE_CHECKING:
    from conversations.manager import ConversationManager


class SystemPromptEditorComponent:
    """Component for editing system prompts."""

    @staticmethod
    def render(manager: "ConversationManager") -> "ConversationManager":
        """
        Render the system prompt editor.

        Args:
            manager: The current conversation manager

        Returns:
            The potentially updated conversation manager
        """
        st.header("System prompt editor")

        # Get current system message
        sys_msg: Message | None = manager.conversation.get_system_message()
        current_sys_prompt: str = sys_msg.content if sys_msg else ""

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

        return manager
