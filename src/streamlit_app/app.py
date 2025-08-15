import streamlit as st

from src.envs import FINANCE_DASHBOARD_ID
from src.streamlit_app.components.config_display import show_configuration
from src.streamlit_app.components.data_editor import display_notion_data_editor
from src.streamlit_app.components.payload_preview import show_notion_payload_preview
from src.streamlit_app.components.validation_display import display_validation_results
from src.streamlit_app.processors.data_loader import load_csv_data
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

    if st.button("📂 Load CSV Data", type="primary"):
        with st.spinner("Loading CSV data..."):
            st.session_state.data_df = load_csv_data()
            st.session_state.edited_data = st.session_state.data_df.copy()
            st.session_state.edited_notion_data = None
            st.session_state.rows_to_delete = set()
        st.rerun()

    if st.session_state.data_df is not None:
        validation_results = validate_data(st.session_state.data_df)

        should_proceed = display_validation_results(validation_results)

        if should_proceed:
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
        st.info("👆 Click 'Load CSV Data' to get started")
        show_configuration()


if __name__ == "__main__":
    main()
