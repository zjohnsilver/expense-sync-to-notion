import os

from dotenv import load_dotenv

load_dotenv()

NOTION_SECRET = os.getenv("NOTION_SECRET")
FINANCE_DASHBOARD_ID = os.getenv("FINANCE_DASHBOARD_ID")
MONTHLY_INVOICE_FILENAME = os.getenv("MONTHLY_INVOICE_FILENAME")

if not NOTION_SECRET:
    raise ValueError("Notion secret isn't provided")

if not FINANCE_DASHBOARD_ID:
    raise ValueError("Finance dashboard ID isn't provided")

if not MONTHLY_INVOICE_FILENAME:
    raise ValueError("Filename isn't provided")
