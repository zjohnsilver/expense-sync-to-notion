from typing import cast

import pandas as pd
import streamlit as st

from src.envs import FINANCE_DASHBOARD_ID
from src.streamlit_app.components.config_display import show_configuration
from src.streamlit_app.components.data_editor import display_notion_data_editor
from src.streamlit_app.components.payload_preview import show_notion_payload_preview
from src.streamlit_app.components.raw_data_editor import display_raw_data_editor
from src.streamlit_app.components.validation_display import display_validation_results
from src.streamlit_app.processors.csv_parser import FileType, parse_uploaded_file
from src.streamlit_app.processors.notion_processor import send_to_notion
from src.streamlit_app.session.state_manager import (
    initialize_session_state,
    reset_session_state,
)
from src.streamlit_app.validators.data_validator import validate_data


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

    with st.sidebar:
        st.header("Data Source")
        file_type = st.selectbox(
            "File Type",
            options=["CREDIT_CARD_INVOICE", "BANK_ACCOUNT_STATEMENT"],
            format_func=lambda x: (
                "Credit Card Invoice"
                if x == "CREDIT_CARD_INVOICE"
                else "Bank Account Statement"
            ),
            index=0 if st.session_state.file_type == "CREDIT_CARD_INVOICE" else 1,
        )
        st.session_state.file_type = file_type
        st.session_state.default_payment_method = (
            "CREDIT_CARD" if file_type == "CREDIT_CARD_INVOICE" else "PIX"
        )

        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded_file is not None:
            with st.spinner("Reading uploaded CSV..."):
                st.session_state.data_df = parse_uploaded_file(
                    uploaded_file, cast(FileType, file_type)
                )
                st.session_state.edited_data = st.session_state.data_df.copy()
                st.session_state.edited_notion_data = None
                st.session_state.rows_to_delete = set()
            st.success("CSV loaded. Proceed below.")

    if st.session_state.data_df is not None:
        # Step 1: Raw data editing; re-runs on any change
        display_raw_data_editor(st.session_state.edited_data)

        # Validate the edited data so row numbers match what's on screen
        validation_results = validate_data(st.session_state.edited_data)

        should_proceed = display_validation_results(validation_results)

        if should_proceed:
            st.divider()
            # Step 2: Notion data preview & editing
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
                            success = send_to_notion(
                                st.session_state.edited_notion_data
                            )

                        if success:
                            st.balloons()
                            reset_session_state()

    else:
        st.info("👈 Upload a CSV in the sidebar to get started")
        show_configuration()


if __name__ == "__main__":
    main()
