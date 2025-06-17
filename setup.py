#!/usr/bin/env python3
"""
Setup script for the Hugging Face integrations package.

This allows you to install the package in development mode:
    pip install -e .

After installation, you can import integrations from anywhere:
    from integrations.openai import OpenAIClient
"""

from setuptools import setup, find_packages
import os

setup(
    name="hugging",
    version="0.1.0",
    packages=find_packages(),
)