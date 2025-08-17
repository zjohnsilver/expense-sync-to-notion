import pandas as pd
import streamlit as st

from src.streamlit_app.processors.notion_processor import transform_data_for_notion


def display_notion_data_editor(df: pd.DataFrame) -> pd.DataFrame:
    """Display and handle the Notion data editor component."""
    if df.empty:
        st.warning("No data to edit")
        return df

    st.subheader("📊 Notion Data Preview & Editing")

    if df.empty:
        st.warning("No data available")
        return df

    notion_data = transform_data_for_notion(df)

    if notion_data.empty:
        return df

    # Add 1-based line numbers for easy error mapping
    notion_data_to_edit = notion_data.copy()
    if notion_data_to_edit.index.min() == 0:
        notion_data_to_edit.index = notion_data_to_edit.index + 1
    notion_data_to_edit.index.name = "Line"

    edited_notion_df = st.data_editor(
        notion_data_to_edit,
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
        hide_index=False,
    )

    st.session_state.edited_notion_data = edited_notion_df

    if len(edited_notion_df) < len(notion_data):
        st.info(
            f"🗑️ {len(notion_data) - len(edited_notion_df)} row(s) removed from the table"
        )

    return df
