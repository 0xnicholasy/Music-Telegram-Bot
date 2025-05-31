#!/bin/bash

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Sync dependencies and create virtual environment
echo "Setting up project with uv..."
uv sync

echo "Setup complete! To activate the virtual environment, run:"
echo "source .venv/bin/activate"
echo ""
echo "To run the bot, use:"
echo "uv run python bot.py" 