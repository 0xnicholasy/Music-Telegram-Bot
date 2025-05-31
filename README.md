# Music Telegram Bot

A Telegram bot for playing music from YouTube playlists.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast dependency management.

### Quick Start

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up the project**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Or manually:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   Create a `.env` file with your Telegram bot token:
   ```
   TOKEN=your_telegram_bot_token_here
   ```

4. **Run the bot**:
   ```bash
   uv run python bot.py
   ```

### Development

- **Add new dependencies**:
  ```bash
  uv add package-name
  ```

- **Add development dependencies**:
  ```bash
  uv add --dev package-name
  ```

- **Update dependencies**:
  ```bash
  uv sync --upgrade
  ```

- **Activate virtual environment** (optional):
  ```bash
  source .venv/bin/activate
  ```

## Usage

Send the bot a YouTube playlist link and it will help you play music from that playlist.

Available commands:
- `/start` - Start the bot
- `/help` - Show help message 