"""
Sidebar Settings Component.

Handles model selection, persona selection, and reasoning toggle.
"""

import streamlit as st
from typing import TYPE_CHECKING
from conversations.types import ChatModel, Persona

if TYPE_CHECKING:
    from conversations.manager import ConversationManager


class SidebarSettingsComponent:
    """Component for managing chat settings in the sidebar."""

    @staticmethod
    def render(manager: "ConversationManager") -> "ConversationManager":
        """
        Render the settings section and handle updates.

        Args:
            manager: The current conversation manager

        Returns:
            The potentially updated conversation manager
        """
        st.header("Settings")

        # Model selection
        updated_manager: ConversationManager = SidebarSettingsComponent._render_model_selection(manager)

        # Persona selection
        updated_manager = SidebarSettingsComponent._render_persona_selection(
            updated_manager
        )

        # Reasoning toggle
        updated_manager = SidebarSettingsComponent._render_reasoning_toggle(
            updated_manager
        )

        return updated_manager

    @staticmethod
    def _render_model_selection(
        manager: "ConversationManager",
    ) -> "ConversationManager":
        """Render model selection dropdown."""
        model_options: list[str] = [m.value for m in ChatModel]
        default_index: int = (
            model_options.index(manager.conversation.settings.model)
            if manager.conversation.settings.model in model_options
            else 0
        )

        selected_model: str = st.selectbox(
            "OpenAI model",
            options=model_options,
            index=default_index,
        )

        if selected_model != manager.conversation.settings.model:
            manager.update_settings(model=selected_model)
            st.rerun()

        return manager

    @staticmethod
    def _render_persona_selection(
        manager: "ConversationManager",
    ) -> "ConversationManager":
        """Render persona selection dropdown."""
        persona_options: list[str] = ["None"] + [p.value for p in Persona]
        current_persona: str | None = manager.conversation.settings.persona

        default_index: int = (
            persona_options.index(current_persona.value) if current_persona else 0
        )

        selected_persona: str = st.selectbox(
            "Assistant persona",
            options=persona_options,
            index=default_index,
        )

        if selected_persona == "None":
            persona_obj: Persona | None = None
        else:
            persona_obj = Persona(selected_persona)

        if persona_obj != manager.conversation.settings.persona:
            manager.update_settings(persona=persona_obj)
            st.rerun()

        return manager

    @staticmethod
    def _render_reasoning_toggle(
        manager: "ConversationManager",
    ) -> "ConversationManager":
        """Render reasoning feature toggle."""
        reasoning_enabled: bool = st.checkbox(
            "🧠 multi-step reasoning",
            value=manager.conversation.settings.reasoning,
        )

        if reasoning_enabled != manager.conversation.settings.reasoning:
            manager.update_settings(reasoning=reasoning_enabled)
            st.rerun()

        return manager
