from datetime import datetime

import pandas as pd

from .base_adapter import BaseInvoiceAdapter, StandardExpenseRow


class NubankAdapter(BaseInvoiceAdapter):
    """Adapter for Nubank invoice format."""

    def read_invoice(self, file_path: str) -> pd.DataFrame:
        """Read Nubank invoice CSV and return standardized DataFrame."""
        # Read Nubank CSV format
        df = pd.read_csv(file_path, sep=",")

        # Convert to standard format
        rows = []
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get("date")) or pd.isna(row.get("title")):
                continue

            # Parse date from Nubank format (YYYY-MM-DD)
            date = datetime.strptime(row["date"], "%Y-%m-%d")

            # Amount is already in float format
            amount = float(row["amount"])

            standard_row = StandardExpenseRow(
                date=date,
                description=str(row["title"]),
                amount=amount,
                category=None,  # Nubank format doesn't include category
            )
            rows.append(standard_row)

        return self._create_standard_dataframe(rows)
