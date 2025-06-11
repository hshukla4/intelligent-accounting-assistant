#!/bin/bash
echo "Running black..."
black --check .

echo "Running isort..."
isort --check-only .

echo "Running flake8..."
flake8
