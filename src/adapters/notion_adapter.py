from datetime import datetime

import pandas as pd

from src.enums import PaymentTypeEnum
from src.notion_gateway import ExpenseRow


class NotionAdapter:
    """Adapter to convert standardized expense data to Notion format."""

    def convert_to_notion_format(
        self,
        df: pd.DataFrame,
        payment_type: PaymentTypeEnum = PaymentTypeEnum.CREDIT_CARD,
    ) -> list[ExpenseRow]:
        """
        Convert standardized DataFrame to list of ExpenseRow objects for Notion.

        Args:
            df: DataFrame with columns: date, description, amount, category
            payment_type: Payment type for all expenses

        Returns:
            List of ExpenseRow objects ready for Notion
        """
        expense_rows = []

        for _, row in df.iterrows():
            expense_row = ExpenseRow(
                date=(
                    row["date"]
                    if isinstance(row["date"], datetime)
                    else datetime.fromisoformat(str(row["date"]))
                ),
                description=str(row["description"]),
                category=row.get("category") or "UNASSIGNED",
                value=float(row["amount"]),
                payment=payment_type.value,
                type_="NON-ESSENTIAL",
                source="AUTOMATION",
            )
            expense_rows.append(expense_row)

        return expense_rows
