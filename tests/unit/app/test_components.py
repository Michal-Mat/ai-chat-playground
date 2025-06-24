import pytest

from conversations.types.enums import ChatModel, Persona, Role


class TestAppComponents:
    """Test individual app components."""

    def test_enum_values_are_valid(self):
        """Test that enum values used in app are valid."""
        # Test ChatModel values
        assert ChatModel.GPT_3_5_TURBO.value == "gpt-3.5-turbo"
        assert ChatModel.GPT_4O.value == "gpt-4o"

        # Test Persona values
        assert Persona.TECHNICAL.value == "technical"
        assert Persona.CREATIVE.value == "creative"

        # Test Role values
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        assert Role.SYSTEM.value == "system"


if __name__ == "__main__":
    pytest.main([__file__])
