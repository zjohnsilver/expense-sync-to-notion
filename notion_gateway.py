from datetime import datetime
from typing import cast

import pandas as pd
import requests
from notion_client import Client

from envs import NOTION_SECRET


class NotionAPIGateway:
    def __init__(self):
        self._notion_client = Client(auth=NOTION_SECRET)
        self.headers = {
            "Authorization": f"Bearer {NOTION_SECRET}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def get_database_all(self, database_id: str) -> pd.DataFrame:
        all_results = []
        next_cursor = None

        while True:
            response = (
                self._notion_client.databases.query(
                    database_id=database_id,
                    start_cursor=next_cursor,
                    page_size=100,
                )
                if next_cursor
                else self._notion_client.databases.query(
                    database_id=database_id, page_size=100
                )
            )
            response = cast(dict, response)

            all_results.extend(response["results"])

            if response.get("has_more"):
                next_cursor = response["next_cursor"]
            else:
                break

        data = []
        for page in all_results:
            props = page["properties"]
            row = {
                key: _extract_property_value(value)
                for key, value in props.items()
            }
            data.append(row)

        return pd.DataFrame(data)

    def insert_row_to_notion(self, payload: dict):
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            print(f"Failed: {response.status_code}, {response.text}")
        else:
            print(
                "Inserted:",
                payload["properties"]["Title"]["title"][0]["text"]["content"],
            )

    @staticmethod
    def build_payload(database_id: str, row: pd.Series) -> dict:
        date_obj = datetime.strptime(row["Data"], "%d/%m/%Y")
        return {
            "parent": {"database_id": database_id},
            "properties": {
                "Month": {"select": {"name": _format_month(date_obj)}},
                "Title": {"title": [{"text": {"content": row["Lançamento"]}}]},
                "Category": {
                    "select": {"name": _get_notion_category(row["Categoria"])}
                },
                "Value": {
                    "number": float(
                        str(row["Valor"]).replace("R$", "").replace(",", ".")
                    )
                },
                "Date": {"date": {"start": date_obj.strftime("%Y-%m-%d")}},
                "Payment": {"select": {"name": "CREDIT_CARD"}},
                "Type": {"select": {"name": "NON-ESSENTIAL"}},
                "SOURCE": {"select": {"name": "AUTOMATION"}},
            },
        }


def _get_notion_category(row: dict) -> str:
    is_amazon = "AMAZON" in row["Lançamento"]

    if is_amazon:
        return "Amazon"

    DEFAULT_CATEGORY = "UNASSIGNED"
    INTER_TO_NOTION_CATEGORY_MAP = {
        "SUPERMERCADO": "Supermarket",
        "DROGARIA": "Health",
    }

    inter_category = row["Categoria"]
    return INTER_TO_NOTION_CATEGORY_MAP.get(inter_category, DEFAULT_CATEGORY)


def _format_month(date: datetime) -> str:
    return date.strftime("%m - %b").upper()


def _extract_property_value(prop):
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
