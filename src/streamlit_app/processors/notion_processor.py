from datetime import datetime
from typing import Dict, List

import pandas as pd
import streamlit as st

from src.envs import FINANCE_DASHBOARD_ID
from src.notion_gateway import NotionAPIGateway, _get_notion_category


def transform_data_for_notion(df: pd.DataFrame) -> pd.DataFrame:
    """Transform CSV data into Notion-compatible format."""
    if df.empty:
        return df

    try:
        if not FINANCE_DASHBOARD_ID:
            st.error("Finance dashboard ID not configured")
            return df

        preview_data = []
        for _, row in df.iterrows():
            try:
                date_obj = datetime.strptime(row["Data"], "%d/%m/%Y")
                month = date_obj.strftime("%m - %b").upper()

                category = _get_notion_category(row)

                value = float(
                    str(row["Valor"]).replace("R$", "").replace(",", ".").strip()
                )

                preview_data.append(
                    {
                        "Month": month,
                        "Bank Description": row["Lançamento"],
                        "Category": category,
                        "Value": f"R$ {value:.2f}".replace(".", ","),
                        "Date": date_obj.strftime("%d/%m/%Y"),
                        "Payment": "CREDIT_CARD",
                        "Type": "NON-ESSENTIAL",
                        "SOURCE": "AUTOMATION",
                    }
                )
            except Exception as e:
                st.error(f"Error processing row: {str(e)}")
                continue

        return pd.DataFrame(preview_data) if preview_data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error creating editable preview: {str(e)}")
        return pd.DataFrame()


def build_notion_payload(row: pd.Series) -> Dict:
    """Build Notion API payload from a data row."""
    return {
        "parent": {"database_id": FINANCE_DASHBOARD_ID},
        "properties": {
            "Month": {"select": {"name": row["Month"]}},
            "Bank Description": {
                "rich_text": [{"text": {"content": row["Bank Description"]}}]
            },
            "Category": {"select": {"name": row["Category"]}},
            "Value": {
                "number": float(
                    str(row["Value"]).replace("R$", "").replace(",", ".").strip()
                )
            },
            "Date": {
                "date": {
                    "start": datetime.strptime(row["Date"], "%d/%m/%Y").strftime(
                        "%Y-%m-%d"
                    )
                }
            },
            "Payment": {"select": {"name": row["Payment"]}},
            "Type": {"select": {"name": row["Type"]}},
            "SOURCE": {"select": {"name": row["SOURCE"]}},
        },
    }


def send_to_notion(data_df: pd.DataFrame) -> bool:
    """Send data to Notion database."""
    if not FINANCE_DASHBOARD_ID:
        st.error("Finance dashboard ID not configured in environment variables")
        return False

    if data_df is None or data_df.empty:
        st.warning("No data to send")
        return False

    notion_gateway = NotionAPIGateway()
    success_count = 0
    error_count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (_, row) in enumerate(data_df.iterrows()):
        try:
            payload = build_notion_payload(row)
            notion_gateway.insert_row_to_notion(payload)
            success_count += 1

            progress = (i + 1) / len(data_df)
            progress_bar.progress(progress)
            status_text.text(f"Processing row {i + 1} of {len(data_df)}...")

        except Exception as e:
            error_count += 1
            st.error(f"Failed to send row {i + 1}: {str(e)}")

    progress_bar.empty()
    status_text.empty()

    if error_count == 0:
        st.success(f"✅ Successfully sent {success_count} rows to Notion!")
        return True
    else:
        st.warning(f"⚠️ Sent {success_count} rows successfully, {error_count} failed")
        return success_count > 0
