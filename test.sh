#!/bin/bash
echo "Running tests"

py3clean .

./scripts/start_dependencies.sh

python -m pytest "$@"
