from datetime import datetime
from typing import Any, Dict

import pandas as pd
import streamlit as st

from src.envs import FINANCE_DASHBOARD_ID, MONTHLY_INVOICE_FILENAME
from src.notion_gateway import NotionAPIGateway


def initialize_session_state():
    if "data_df" not in st.session_state:
        st.session_state.data_df = None
    if "edited_data" not in st.session_state:
        st.session_state.edited_data = None
    if "edited_notion_data" not in st.session_state:
        st.session_state.edited_notion_data = None
    if "rows_to_delete" not in st.session_state:
        st.session_state.rows_to_delete = set()


def load_csv_data() -> pd.DataFrame:
    if not MONTHLY_INVOICE_FILENAME:
        st.error("Monthly invoice filename not configured in environment variables")
        st.stop()
    try:
        df = pd.read_csv(MONTHLY_INVOICE_FILENAME, sep=",")
        return df
    except FileNotFoundError:
        st.error(f"CSV file not found: {MONTHLY_INVOICE_FILENAME}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        st.stop()


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    validation_results = {"is_valid": True, "errors": [], "warnings": []}

    required_columns = ["Data", "Lançamento", "Categoria", "Tipo", "Valor"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        validation_results["is_valid"] = False
        validation_results["errors"].append(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    for idx, row in df.iterrows():
        try:
            datetime.strptime(row["Data"], "%d/%m/%Y")
        except (ValueError, TypeError):
            row_num = idx + 1 if isinstance(idx, int) else str(idx)
            validation_results["warnings"].append(
                f"Row {row_num}: Invalid date format '{row['Data']}' (expected DD/MM/YYYY)"
            )

    for idx, row in df.iterrows():
        try:
            value_str = str(row["Valor"]).replace("R$", "").replace(",", ".").strip()
            float(value_str)
        except (ValueError, TypeError):
            row_num = idx + 1 if isinstance(idx, int) else str(idx)
            validation_results["warnings"].append(
                f"Row {row_num}: Invalid value format '{row['Valor']}'"
            )

    return validation_results


def display_notion_data_editor(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        st.warning("No data to edit")
        return df

    st.subheader("📊 Notion Data Preview & Editing")

    if df.empty:
        st.warning("No data available")
        return df

    try:
        if not FINANCE_DASHBOARD_ID:
            st.error("Finance dashboard ID not configured")
            return df

        from src.notion_gateway import _get_notion_category

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

        if preview_data:
            preview_df = pd.DataFrame(preview_data)

            edited_notion_df = st.data_editor(
                preview_df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "Month": st.column_config.TextColumn("Month", width="small"),
                    "Bank Description": st.column_config.TextColumn(
                        "Description", width="large"
                    ),
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        width="medium",
                        options=[
                            "Amazon",
                            "Supermarket",
                            "Health",
                            "UNASSIGNED",
                            "Subscription",
                            "Others",
                            "Home",
                            "Food",
                            "Food[Ifood]",
                        ],
                        required=True,
                    ),
                    "Value": st.column_config.TextColumn("Value", width="small"),
                    "Date": st.column_config.TextColumn("Date", width="small"),
                    "Payment": st.column_config.SelectboxColumn(
                        "Payment",
                        width="small",
                        options=["CREDIT_CARD", "DEBIT_CARD", "CASH", "PIX"],
                        required=True,
                    ),
                    "Type": st.column_config.SelectboxColumn(
                        "Type",
                        width="medium",
                        options=["ESSENTIAL", "NON-ESSENTIAL", "INVESTMENT"],
                        required=True,
                    ),
                    "SOURCE": st.column_config.SelectboxColumn(
                        "Source",
                        width="small",
                        options=["AUTOMATION", "MANUAL"],
                        required=True,
                    ),
                },
                key="notion_data_editor",
            )

            st.session_state.edited_notion_data = edited_notion_df

            if len(edited_notion_df) < len(preview_df):
                st.info(
                    f"🗑️ {len(preview_df) - len(edited_notion_df)} row(s) removed from the table"
                )

    except Exception as e:
        st.error(f"Error creating editable preview: {str(e)}")

    return df


def show_notion_payload_preview():
    if (
        st.session_state.edited_notion_data is None
        or st.session_state.edited_notion_data.empty
    ):
        return

    with st.expander("🔧 Sample Notion API Payloads (first 3 rows)"):
        for i, (_, row) in enumerate(
            st.session_state.edited_notion_data.head(3).iterrows()
        ):
            try:
                payload = {
                    "parent": {"database_id": FINANCE_DASHBOARD_ID},
                    "properties": {
                        "Month": {"select": {"name": row["Month"]}},
                        "Bank Description": {
                            "rich_text": [
                                {"text": {"content": row["Bank Description"]}}
                            ]
                        },
                        "Category": {"select": {"name": row["Category"]}},
                        "Value": {
                            "number": float(
                                str(row["Value"])
                                .replace("R$", "")
                                .replace(",", ".")
                                .strip()
                            )
                        },
                        "Date": {
                            "date": {
                                "start": datetime.strptime(
                                    row["Date"], "%d/%m/%Y"
                                ).strftime("%Y-%m-%d")
                            }
                        },
                        "Payment": {"select": {"name": row["Payment"]}},
                        "Type": {"select": {"name": row["Type"]}},
                        "SOURCE": {"select": {"name": row["SOURCE"]}},
                    },
                }
                st.json(payload)
                if i < 2:
                    st.divider()
            except Exception as e:
                st.error(f"Error building payload for row {i+1}: {str(e)}")


def send_to_notion() -> bool:
    if not FINANCE_DASHBOARD_ID:
        st.error("Finance dashboard ID not configured in environment variables")
        return False

    if (
        st.session_state.edited_notion_data is None
        or st.session_state.edited_notion_data.empty
    ):
        st.warning("No data to send")
        return False

    notion_gateway = NotionAPIGateway()
    success_count = 0
    error_count = 0

    final_data = st.session_state.edited_notion_data

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (_, row) in enumerate(final_data.iterrows()):
        try:
            payload = {
                "parent": {"database_id": FINANCE_DASHBOARD_ID},
                "properties": {
                    "Month": {"select": {"name": row["Month"]}},
                    "Bank Description": {
                        "rich_text": [{"text": {"content": row["Bank Description"]}}]
                    },
                    "Category": {"select": {"name": row["Category"]}},
                    "Value": {
                        "number": float(
                            str(row["Value"])
                            .replace("R$", "")
                            .replace(",", ".")
                            .strip()
                        )
                    },
                    "Date": {
                        "date": {
                            "start": datetime.strptime(
                                row["Date"], "%d/%m/%Y"
                            ).strftime("%Y-%m-%d")
                        }
                    },
                    "Payment": {"select": {"name": row["Payment"]}},
                    "Type": {"select": {"name": row["Type"]}},
                    "SOURCE": {"select": {"name": row["SOURCE"]}},
                },
            }

            notion_gateway.insert_row_to_notion(payload)
            success_count += 1

            progress = (i + 1) / len(final_data)
            progress_bar.progress(progress)
            status_text.text(f"Processing row {i + 1} of {len(final_data)}...")

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


def main():
    st.set_page_config(
        page_title="Expense Sync to Notion",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("💰 Expense Sync to Notion")
    st.markdown("Review, edit, and validate your expense data before syncing to Notion")

    initialize_session_state()

    if st.button("📂 Load CSV Data", type="primary"):
        with st.spinner("Loading CSV data..."):
            st.session_state.data_df = load_csv_data()
            st.session_state.edited_data = st.session_state.data_df.copy()
            st.session_state.edited_notion_data = None
            st.session_state.rows_to_delete = set()
        st.rerun()

    if st.session_state.data_df is not None:
        validation_results = validate_data(st.session_state.data_df)

        if not validation_results["is_valid"]:
            st.error("❌ Data validation failed:")
            for error in validation_results["errors"]:
                st.error(f"• {error}")

        if validation_results["warnings"]:
            st.warning("⚠️ Data validation warnings:")
            for warning in validation_results["warnings"]:
                st.warning(f"• {warning}")

        if validation_results["is_valid"] or st.checkbox(
            "Proceed despite validation errors"
        ):
            display_notion_data_editor(st.session_state.edited_data)

            if (
                st.session_state.edited_notion_data is not None
                and not st.session_state.edited_notion_data.empty
            ):
                show_notion_payload_preview()

            st.divider()

            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                if st.button(
                    "🚀 Send to Notion", type="primary", use_container_width=True
                ):
                    if not FINANCE_DASHBOARD_ID:
                        st.error("Finance dashboard ID not configured")
                    elif (
                        st.session_state.edited_notion_data is None
                        or st.session_state.edited_notion_data.empty
                    ):
                        st.error("No data to send. Please load and edit data first.")
                    else:
                        with st.spinner("Sending data to Notion..."):
                            success = send_to_notion()

                        if success:
                            st.balloons()
                            st.session_state.data_df = None
                            st.session_state.edited_data = None
                            st.session_state.edited_notion_data = None
                            st.session_state.rows_to_delete = set()

    else:
        st.info("👆 Click 'Load CSV Data' to get started")

        with st.expander("Configuration"):
            st.write(
                "**Monthly Invoice Filename:**",
                MONTHLY_INVOICE_FILENAME or "Not configured",
            )
            st.write(
                "**Finance Dashboard ID:**", FINANCE_DASHBOARD_ID or "Not configured"
            )


if __name__ == "__main__":
    main()
