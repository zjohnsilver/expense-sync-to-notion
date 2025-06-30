import os

from dotenv import load_dotenv

load_dotenv()

NOTION_SECRET = os.getenv("NOTION_SECRET")
FINANCE_DASHBOARD_ID = os.getenv("FINANCE_DASHBOARD_ID")
MONTHLY_INVOICE_FILENAME = os.getenv("MONTHLY_INVOICE_FILENAME")
