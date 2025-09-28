from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypedDict, cast

import pandas as pd
from notion_client import Client

from src.envs import NOTION_SECRET

from src.enums import PaymentTypeEnum


@dataclass
class ExpenseRow:
    date: datetime
    description: str
    category: str
    value: float
    payment: str
    type_: str
    source: str = "AUTOMATION"

    @classmethod
    def from_series(cls, row: pd.Series, payment_type: PaymentTypeEnum) -> "ExpenseRow":
        return cls(
            date=datetime.strptime(row["Data"], "%d/%m/%Y"),
            description=str(row["Lançamento"]),
            category=row.get("NewCategory") or row.get("Categoria") or "UNASSIGNED",
            value=float(
                str(row["Valor"]).replace("R$", "").replace(".", "").replace(",", ".")
            ),
            payment=payment_type.value,
            type_="NON-ESSENTIAL",
        )


class NotionPayload(TypedDict):
    parent: dict[str, str]
    properties: dict[str, Any]


class NotionAPIGateway:
    def __init__(self) -> None:
        self._notion_client = Client(auth=NOTION_SECRET)

    def get_database_all(self, database_id: str) -> pd.DataFrame:
        all_results: list[dict[str, Any]] = []
        next_cursor: str | None = None

        while True:
            response = (
                self._notion_client.databases.query(
                    database_id=database_id,
                    start_cursor=next_cursor,
                    page_size=100,
                )
                if next_cursor
                else self._notion_client.databases.query(
                    database_id=database_id,
                    page_size=100,
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
            row = {key: _extract_property_value(value) for key, value in props.items()}
            data.append(row)

        return pd.DataFrame(data)

    def send_row_to_notion(self, database_id: str, expense: ExpenseRow) -> None:
        payload = self.build_payload(database_id, expense)
        self._notion_client.pages.create(**payload)

    def send_payloads(self, payloads: list[NotionPayload]) -> None:
        for idx, payload in enumerate(payloads, start=1):
            print("\n" + "-" * 200 + "\n")
            print(f"[{idx}] Sending payload -> {payload}")
            try:
                self._notion_client.pages.create(**payload)
                # pass
            except Exception as e:
                print(f"[{idx}] Failed to send: {e}")

    @staticmethod
    def build_payload(database_id: str, expense: ExpenseRow) -> NotionPayload:
        return {
            "parent": {"database_id": database_id},
            "properties": {
                "Month": {"select": {"name": _format_month(expense.date)}},
                "Bank Description": {
                    "rich_text": [{"text": {"content": expense.description}}]
                },
                "Category": {"select": {"name": expense.category}},
                "Value": {"number": expense.value},
                "Date": {"date": {"start": expense.date.strftime("%Y-%m-%d")}},
                "Payment": {"select": {"name": expense.payment}},
                "Type": {"select": {"name": expense.type_}},
                "SOURCE": {"select": {"name": expense.source}},
            },
        }


def _format_month(date: datetime) -> str:
    # return date.strftime("%m - %b").upper()
    return "10 - OCT"


def _extract_property_value(prop: dict[str, Any]) -> Any:
    match prop["type"]:
        case "title":
            return prop["title"][0]["plain_text"] if prop["title"] else None
        case "rich_text":
            return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else None
        case "number":
            return prop["number"]
        case "select":
            return prop["select"]["name"] if prop["select"] else None
        case "multi_select":
            return [s["name"] for s in prop["multi_select"]]
        case "date":
            return prop["date"]["start"] if prop["date"] else None
        case "formula":
            return prop["formula"].get("string") or prop["formula"].get("number")
        case _:
            return str(prop.get(prop["type"]))
