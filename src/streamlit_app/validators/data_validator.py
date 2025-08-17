from datetime import datetime
from typing import Any, Dict

import pandas as pd


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate the CSV data for required columns and formats."""
    validation_results = {"is_valid": True, "errors": [], "warnings": []}

    required_columns = ["Data", "Lançamento", "Categoria", "Valor"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        validation_results["is_valid"] = False
        validation_results["errors"].append(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Optional column checks
    if "Tipo" not in df.columns:
        validation_results["warnings"].append("Optional column missing: Tipo")

    # Determine if index is already 1-based (from UI editors)
    try:
        index_is_one_based = int(getattr(df.index, "min", lambda: 0)()) == 1  # type: ignore[attr-defined]
    except Exception:
        index_is_one_based = False
    index_offset = 0 if index_is_one_based else 1

    for idx, row in df.iterrows():
        try:
            datetime.strptime(row["Data"], "%d/%m/%Y")
        except (ValueError, TypeError):
            row_num = (idx + index_offset) if isinstance(idx, int) else str(idx)
            validation_results["warnings"].append(
                f"Row {row_num}: Invalid date format '{row['Data']}' (expected DD/MM/YYYY)"
            )

    for idx, row in df.iterrows():
        try:
            value_str = str(row["Valor"]).replace("R$", "").replace(",", ".").strip()
            float(value_str)
        except (ValueError, TypeError):
            row_num = (idx + index_offset) if isinstance(idx, int) else str(idx)
            validation_results["warnings"].append(
                f"Row {row_num}: Invalid value format '{row['Valor']}'"
            )

    return validation_results
