from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import pandas as pd


@dataclass
class StandardExpenseRow:
    """Standardized expense row format that all adapters should produce."""

    date: datetime
    description: str
    amount: float
    category: str | None = None


class InvoiceAdapter(Protocol):
    """Protocol for invoice adapters."""

    def read_invoice(self, file_path: str) -> pd.DataFrame:
        """Read invoice file and return standardized DataFrame."""
        ...


class BaseInvoiceAdapter(ABC):
    """Base class for invoice adapters."""

    @abstractmethod
    def read_invoice(self, file_path: str) -> pd.DataFrame:
        """
        Read invoice file and return standardized DataFrame.

        Returns DataFrame with columns:
        - date: datetime
        - description: str
        - amount: float
        - category: str (optional, can be None)
        """
        pass

    def _create_standard_dataframe(
        self, rows: list[StandardExpenseRow]
    ) -> pd.DataFrame:
        """Create standardized DataFrame from StandardExpenseRow objects."""
        return pd.DataFrame(
            [
                {
                    "date": row.date,
                    "description": row.description,
                    "amount": row.amount,
                    "category": row.category,
                }
                for row in rows
            ]
        )
