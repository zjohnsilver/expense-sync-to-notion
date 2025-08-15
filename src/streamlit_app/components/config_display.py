import streamlit as st

from src.envs import FINANCE_DASHBOARD_ID, MONTHLY_INVOICE_FILENAME


def show_configuration():
    """Display the current configuration in an expander."""
    with st.expander("Configuration"):
        st.write(
            "**Monthly Invoice Filename:**",
            MONTHLY_INVOICE_FILENAME or "Not configured",
        )
        st.write("**Finance Dashboard ID:**", FINANCE_DASHBOARD_ID or "Not configured")
