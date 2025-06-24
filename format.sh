#!/bin/bash
# Script to format and lint the codebase

echo "🔧 Running black formatter..."
black .

echo "🔍 Running ruff linter with auto-fix..."
ruff check . --fix

echo "📝 Running ruff formatter..."
ruff format .

echo "✅ Code formatting and linting complete!"
