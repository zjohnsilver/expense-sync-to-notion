from typing import Any, Dict

import streamlit as st


def display_validation_results(validation_results: Dict[str, Any]) -> bool:
    """Display validation results and return whether to proceed."""
    if not validation_results["is_valid"]:
        st.error("❌ Data validation failed:")
        for error in validation_results["errors"]:
            st.error(f"• {error}")

    if validation_results["warnings"]:
        st.warning("⚠️ Data validation warnings:")
        for warning in validation_results["warnings"]:
            st.warning(f"• {warning}")

    return validation_results["is_valid"] or st.checkbox(
        "Proceed despite validation errors"
    )
