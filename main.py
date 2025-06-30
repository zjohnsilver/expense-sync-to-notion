from pprint import pprint

import pandas as pd

from envs import FINANCE_DASHBOARD_ID, MONTHLY_INVOICE_FILENAME
from notion_gateway import NotionAPIGateway

notion_api_gateway = NotionAPIGateway()


if not FINANCE_DASHBOARD_ID:
    raise ValueError("Finance dashboard ID not provided")

if not MONTHLY_INVOICE_FILENAME:
    raise ValueError("Filename it's not provided")

monthly_invoice_df = pd.read_csv(MONTHLY_INVOICE_FILENAME, sep=",")

for _, row in monthly_invoice_df.iterrows():
    payload = NotionAPIGateway.build_payload(
        database_id=FINANCE_DASHBOARD_ID, row=row
    )
    pprint(payload, indent=4)
    print("\n")
    # notion_api_gateway.insert_row_to_notion(payload)

print(monthly_invoice_df)
