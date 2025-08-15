import streamlit as st


def initialize_session_state():
    """Initialize all required session state variables."""
    if "data_df" not in st.session_state:
        st.session_state.data_df = None
    if "edited_data" not in st.session_state:
        st.session_state.edited_data = None
    if "edited_notion_data" not in st.session_state:
        st.session_state.edited_notion_data = None
    if "rows_to_delete" not in st.session_state:
        st.session_state.rows_to_delete = set()


def reset_session_state():
    """Reset session state after successful sync."""
    st.session_state.data_df = None
    st.session_state.edited_data = None
    st.session_state.edited_notion_data = None
    st.session_state.rows_to_delete = set()
