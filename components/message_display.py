"""
Message Display Component.

Handles rendering of chat messages with proper formatting.
"""

from typing import TYPE_CHECKING

import streamlit as st

from conversations.types import Role

if TYPE_CHECKING:
    from conversations.models.models import Message


class MessageDisplayComponent:
    """Component for displaying chat messages."""

    @staticmethod
    def render_messages(messages: list["Message"]) -> None:
        """
        Render all chat messages.

        Args:
            messages: List of messages to display
        """
        for message in messages:
            MessageDisplayComponent.render_message(message)

    @staticmethod
    def render_message(message: "Message") -> None:
        """
        Render a single chat message.

        Args:
            message: The message to render
        """
        if message.role == Role.SYSTEM:
            MessageDisplayComponent._render_system_message(message)
        elif message.role == Role.ASSISTANT:
            MessageDisplayComponent._render_assistant_message(message)
        else:
            MessageDisplayComponent._render_user_message(message)

    @staticmethod
    def _render_system_message(message: "Message") -> None:
        """
        Render a system message.

        Args:
            message: The system message to render
        """
        st.chat_message("assistant").markdown(
            f"🎯 _System prompt:_ {message.content}"
        )

    @staticmethod
    def _render_user_message(message: "Message") -> None:
        """
        Render a user message.

        Args:
            message: The user message to render
        """
        st.chat_message("user").markdown(message.content)

    @staticmethod
    def _render_assistant_message(message: "Message") -> None:
        """
        Render an assistant message with model and token info.

        Args:
            message: The assistant message to render
        """
        # Build the metadata tag
        tag = MessageDisplayComponent._build_metadata_tag(message)

        # Build the content
        content = f"*_{tag}_*\n\n{message.content}"

        # Check if this is a reasoning message
        if MessageDisplayComponent._is_reasoning_message(message):
            MessageDisplayComponent._render_reasoning_message(content)
        else:
            st.chat_message("assistant").markdown(content)

    @staticmethod
    def _build_metadata_tag(message: "Message") -> str:
        """
        Build the metadata tag for assistant messages.

        Args:
            message: The message to build metadata for

        Returns:
            The formatted metadata tag
        """
        tag_parts = []

        if message.model:
            tag_parts.append(message.model)

        if message.persona:
            tag_parts.append(f"persona: {message.persona}")

        if message.token_count and message.token_count > 0:
            tag_parts.append(f"{message.token_count} tokens")

        return " · ".join(tag_parts) if tag_parts else "assistant"

    @staticmethod
    def _is_reasoning_message(message: "Message") -> bool:
        """
        Detect if this is a reasoning message.

        Args:
            message: The message to check

        Returns:
            True if this appears to be a reasoning message
        """
        reasoning_markers = (
            "**Task summary:**",
            "**Proposed steps:**",
            "### Step",
        )

        body = message.content
        return any(
            body.lstrip().startswith(marker) for marker in reasoning_markers
        )

    @staticmethod
    def _render_reasoning_message(content: str) -> None:
        """
        Render a reasoning message with special styling.

        Args:
            content: The formatted content to render
        """
        # Render in smaller gray font so it doesn't dominate the UI
        html_start = "<div style='font-size:0.85em; color:gray;'>"
        html_end = "</div>"
        converted = content.replace("\n", "<br/>")
        styled = html_start + converted + html_end

        st.chat_message("assistant").markdown(styled, unsafe_allow_html=True)
