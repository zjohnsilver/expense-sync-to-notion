import pandas as pd
import streamlit as st


def display_raw_data_editor(df: pd.DataFrame) -> pd.DataFrame:
    """Allow the user to review and edit the raw uploaded data before transformation."""
    if df.empty:
        st.warning("No data to edit")
        return df

    st.subheader("🧾 Raw Data Review & Editing")

    # Ensure 1-based line numbering is visible and preserved
    df_to_edit = df.copy()
    if df_to_edit.index.min() == 0:
        df_to_edit.index = df_to_edit.index + 1
    df_to_edit.index.name = "Line"

    edited_df = st.data_editor(
        df_to_edit,
        use_container_width=True,
        num_rows="dynamic",
        key="raw_data_editor",
        hide_index=False,
    )

    st.session_state.edited_data = edited_df
    return edited_df
