from datetime import datetime

import pandas as pd

from .base_adapter import BaseInvoiceAdapter, StandardExpenseRow


class InterAdapter(BaseInvoiceAdapter):
    """Adapter for Inter bank invoice format."""

    def read_invoice(self, file_path: str) -> pd.DataFrame:
        """Read Inter invoice CSV and return standardized DataFrame."""
        # Read Inter CSV format
        df = pd.read_csv(file_path, sep=",")

        # Convert to standard format
        rows = []
        for _, row in df.iterrows():
            # Parse date from Inter format (DD/MM/YYYY)
            date = datetime.strptime(row["Data"], "%d/%m/%Y")

            # Clean amount value (remove R$, dots, and replace comma with dot)
            amount_str = (
                str(row["Valor"])
                .replace("R$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            amount = float(amount_str)

            standard_row = StandardExpenseRow(
                date=date,
                description=str(row["Lançamento"]),
                amount=amount,
                category=row.get("Categoria"),
            )
            rows.append(standard_row)

        return self._create_standard_dataframe(rows)
