"""
OpenAI Integration Module

This module provides a convenient wrapper around the OpenAI API
that handles authentication via environment variables.
"""

from .client import OpenAIClient, create_openai_client

__all__ = ["OpenAIClient", "create_openai_client"]
