from core.container import get_container, reset_container


class TestServiceContainer:
    """Test the service container itself."""

    def setup_method(self):
        """Reset container for each test."""
        reset_container()

    def test_singleton_behavior(self):
        """Test that singletons return the same instance."""
        container = get_container()

        # Register a singleton
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        container.register_singleton("test_service", factory)

        # Get service multiple times
        instance1 = container.get("test_service")
        instance2 = container.get("test_service")

        # Should be same instance
        assert instance1 == instance2 == "instance_1"
        assert call_count == 1  # Factory called only once

    def test_factory_behavior(self):
        """Test that factories return new instances."""
        container = get_container()

        # Register a factory
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        container.register_factory("test_service", factory)

        # Get service multiple times
        instance1 = container.get("test_service")
        instance2 = container.get("test_service")

        # Should be different instances
        assert instance1 == "instance_1"
        assert instance2 == "instance_2"
        assert call_count == 2  # Factory called twice
