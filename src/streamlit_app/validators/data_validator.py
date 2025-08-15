from datetime import datetime
from typing import Any, Dict

import pandas as pd


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate the CSV data for required columns and formats."""
    validation_results = {"is_valid": True, "errors": [], "warnings": []}

    required_columns = ["Data", "Lançamento", "Categoria", "Tipo", "Valor"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        validation_results["is_valid"] = False
        validation_results["errors"].append(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    for idx, row in df.iterrows():
        try:
            datetime.strptime(row["Data"], "%d/%m/%Y")
        except (ValueError, TypeError):
            row_num = idx + 1 if isinstance(idx, int) else str(idx)
            validation_results["warnings"].append(
                f"Row {row_num}: Invalid date format '{row['Data']}' (expected DD/MM/YYYY)"
            )

    for idx, row in df.iterrows():
        try:
            value_str = str(row["Valor"]).replace("R$", "").replace(",", ".").strip()
            float(value_str)
        except (ValueError, TypeError):
            row_num = idx + 1 if isinstance(idx, int) else str(idx)
            validation_results["warnings"].append(
                f"Row {row_num}: Invalid value format '{row['Valor']}'"
            )

    return validation_results
