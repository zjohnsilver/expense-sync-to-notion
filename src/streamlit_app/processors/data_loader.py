import pandas as pd
import streamlit as st

from src.envs import MONTHLY_INVOICE_FILENAME


def load_csv_data() -> pd.DataFrame:
    """Load CSV data from the configured monthly invoice file."""
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
