import os

import pandas as pd
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_SECRET = os.getenv("NOTION_SECRET")
FINANCE_DASHBOARD_ID = os.getenv("FINANCE_DASHBOARD_ID")

notion = Client(auth=NOTION_SECRET)

database_id = FINANCE_DASHBOARD_ID


def extract_property_value(prop):
    type_ = prop["type"]

    if type_ == "title":
        return prop["title"][0]["plain_text"] if prop["title"] else None
    elif type_ == "rich_text":
        return (
            prop["rich_text"][0]["plain_text"] if prop["rich_text"] else None
        )
    elif type_ == "number":
        return prop["number"]
    elif type_ == "select":
        return prop["select"]["name"] if prop["select"] else None
    elif type_ == "multi_select":
        return [s["name"] for s in prop["multi_select"]]
    elif type_ == "date":
        return prop["date"]["start"] if prop["date"] else None
    elif type_ == "formula":
        return prop["formula"].get("string") or prop["formula"].get("number")
    else:
        return str(prop.get(type_))


# Read database Finance dashboard into dataframe
all_results = []
next_cursor = None

while True:
    response = (
        notion.databases.query(
            database_id=database_id, start_cursor=next_cursor, page_size=100
        )
        if next_cursor
        else notion.databases.query(database_id=database_id, page_size=100)
    )

    all_results.extend(response["results"])

    if response.get("has_more"):
        next_cursor = response["next_cursor"]
    else:
        break

# Build DataFrame
data = []
for page in all_results:
    props = page["properties"]
    row = {key: extract_property_value(value) for key, value in props.items()}
    data.append(row)

df = pd.DataFrame(data)
print(df)
breakpoint()
