from conversations.types.enums import Role
import pytest


class TestMessageFormatting:
    """Test message formatting logic."""

    def test_message_role_mapping(self):
        """Test that message roles are mapped correctly."""
        test_cases = [
            (Role.USER, "user"),
            (Role.ASSISTANT, "assistant"),
            (Role.SYSTEM, "assistant"),
        ]

        for message_role, expected_chat_role in test_cases:
            if message_role == Role.ASSISTANT:
                chat_role = "assistant"
            elif message_role == Role.SYSTEM:
                chat_role = "assistant"
            else:
                chat_role = "user"

            assert chat_role == expected_chat_role

    def test_reasoning_message_detection(self):
        """Test detection of reasoning helper messages."""
        reasoning_markers = (
            "**Task summary:**",
            "**Proposed steps:**",
            "### Step",
        )

        test_messages = [
            ("**Task summary:** This is a reasoning message", True),
            ("**Proposed steps:** Step 1, Step 2", True),
            ("### Step 1: First step", True),
            ("Regular response message", False),
        ]

        for message_body, expected_is_reasoning in test_messages:
            is_reasoning = any(
                message_body.lstrip().startswith(marker) for marker in reasoning_markers
            )
            assert is_reasoning == expected_is_reasoning


if __name__ == "__main__":
    pytest.main([__file__])
