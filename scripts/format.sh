#!/bin/bash
# Script to format and lint the codebase

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root to run commands
cd "$PROJECT_ROOT"

echo "🔍 Running ruff linter with auto-fix..."
ruff check . --fix

echo "🔧 Running ruff formatter..."
ruff format .

echo "✅ Code formatting and linting complete!"
