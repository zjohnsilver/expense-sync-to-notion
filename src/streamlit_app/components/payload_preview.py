import streamlit as st

from src.streamlit_app.processors.notion_processor import build_notion_payload


def show_notion_payload_preview():
    """Display preview of Notion API payloads for the first few rows."""
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
                payload = build_notion_payload(row)
                st.json(payload)
                if i < 2:
                    st.divider()
            except Exception as e:
                st.error(f"Error building payload for row {i+1}: {str(e)}")
