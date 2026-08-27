#!/bin/bash
# Wrapper script to run plotting scripts with correct PYTHONPATH

cd "$(dirname "$0")"
export PYTHONPATH="${PWD}/src/python:${PYTHONPATH}"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <plot_script_name>"
    echo ""
    echo "Available plotting scripts:"
    ls -1 src/python/plotting/*.py | sed 's|src/python/plotting/||' | sed 's|\.py$||'
    exit 1
fi

SCRIPT_NAME="$1"
if [[ ! "$SCRIPT_NAME" == *.py ]]; then
    SCRIPT_NAME="${SCRIPT_NAME}.py"
fi

if [ -f "src/python/plotting/${SCRIPT_NAME}" ]; then
    python3 -m "plotting.${SCRIPT_NAME%.py}"
else
    echo "Error: Script not found: src/python/plotting/${SCRIPT_NAME}"
    exit 1
fi
