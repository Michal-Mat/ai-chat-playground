"""
Chat Input Component.

Handles user input and AI response processing.
"""

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from conversations.manager import ConversationManager


class ChatInputComponent:
    """Component for handling chat input and responses."""

    @staticmethod
    def render(manager: "ConversationManager") -> "ConversationManager":
        """
        Render the chat input and handle responses.

        Args:
            manager: The current conversation manager

        Returns:
            The potentially updated conversation manager
        """
        if prompt := st.chat_input("What would you like to discuss?"):
            ChatInputComponent._handle_user_input(manager, prompt)

        return manager

    @staticmethod
    def _handle_user_input(
        manager: "ConversationManager", prompt: str
    ) -> None:
        """
        Handle user input and generate AI response.

        Args:
            manager: The conversation manager
            prompt: The user's input prompt
        """
        # Show user message
        st.chat_message("user").markdown(prompt)

        # Get AI response (blocking)
        with st.spinner("Thinking..."):
            try:
                answer = manager.chat(prompt)
                last_msg = manager.get_messages()[-1]

                # Build metadata tag
                tag_parts = []

                model_label = getattr(
                    last_msg,
                    "model",
                    manager.conversation.settings.model,
                )
                if model_label:
                    tag_parts.append(model_label)

                persona_resp = getattr(last_msg, "persona", None)
                if persona_resp:
                    tag_parts.append(f"persona: {persona_resp}")

                token_count_resp = getattr(last_msg, "token_count", None)
                if token_count_resp:
                    tag_parts.append(f"{token_count_resp} tokens")

                tag = " · ".join(tag_parts) if tag_parts else "assistant"

                st.chat_message("assistant").markdown(f"*_{tag}_*\n\n{answer}")

            except Exception as exc:
                error_text = (
                    f"⚠️ **Error calling OpenAI:** {exc}\n\n"
                    "Please revise your prompt or choose a different model and "
                    "try again."
                )
                st.chat_message("assistant").markdown(error_text)
