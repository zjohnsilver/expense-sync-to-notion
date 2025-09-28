import subprocess
import sys
from pathlib import Path

import click

from src.notion_sync_expenses.notion_sync_service import NotionSyncService


@click.group()
def cli():
    """💰 Expense Sync to Notion CLI."""


@cli.command()
def streamlit():
    """Launch the Streamlit interface."""
    streamlit_app_path = Path(__file__).parent / "streamlit_app" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_app_path)])


@cli.command()
def sync():
    """Run direct sync (send expenses to Notion)."""
    notion_sync_service = NotionSyncService()
    notion_sync_service.sync_expenses()


if __name__ == "__main__":
    cli()
