#!/bin/bash
echo "Running tests"

py3clean .

python -m pytest "$@"
