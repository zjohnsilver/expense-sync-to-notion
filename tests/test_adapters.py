"""Test cases for invoice adapters."""

import pytest
from datetime import datetime
from pathlib import Path

from src.adapters.adapter_factory import AdapterFactory
from src.adapters.notion_adapter import NotionAdapter
from src.enums import PaymentTypeEnum, BankEnum


class TestAdapterFactory:
    """Test cases for AdapterFactory."""

    def test_create_inter_adapter(self):
        """Test creating Inter adapter."""
        adapter = AdapterFactory.create_adapter("INTER")
        assert adapter is not None

    def test_create_nubank_adapter(self):
        """Test creating Nubank adapter."""
        adapter = AdapterFactory.create_adapter("NUBANK")
        assert adapter is not None

    def test_unsupported_bank_raises_error(self):
        """Test that unsupported bank raises ValueError."""
        with pytest.raises(ValueError, match="is not a valid BankEnum"):
            AdapterFactory.create_adapter("INVALID_BANK")

    def test_get_supported_banks(self):
        """Test getting supported banks list."""
        banks = AdapterFactory.get_supported_banks()
        assert BankEnum.INTER.value in banks
        assert BankEnum.NUBANK.value in banks


class TestInterAdapter:
    """Test cases for Inter adapter."""

    def test_read_inter_invoice(self):
        """Test reading Inter invoice format."""
        adapter = AdapterFactory.create_adapter("INTER")

        # Use the existing fatura.csv file
        df = adapter.read_invoice("fatura.csv")

        # Verify DataFrame structure
        assert not df.empty
        assert "date" in df.columns
        assert "description" in df.columns
        assert "amount" in df.columns
        assert "category" in df.columns

        # Verify data types
        first_row = df.iloc[0]
        assert isinstance(first_row["date"], datetime)
        assert isinstance(first_row["description"], str)
        assert isinstance(first_row["amount"], float)

        # Verify some expected data from fatura.csv
        assert len(df) > 0

    def test_inter_amount_parsing(self):
        """Test that Inter amounts are parsed correctly."""
        adapter = AdapterFactory.create_adapter("INTER")
        df = adapter.read_invoice("fatura.csv")

        # All amounts should be positive floats
        for amount in df["amount"]:
            assert isinstance(amount, float)
            assert amount > 0


class TestNubankAdapter:
    """Test cases for Nubank adapter."""

    def test_read_nubank_invoice(self):
        """Test reading Nubank invoice format."""
        adapter = AdapterFactory.create_adapter("NUBANK")

        # Use the existing Nubank CSV file
        df = adapter.read_invoice("Nubank_2025-10-07.csv")

        # Verify DataFrame structure
        assert not df.empty
        assert "date" in df.columns
        assert "description" in df.columns
        assert "amount" in df.columns
        assert "category" in df.columns

        # Verify data types
        first_row = df.iloc[0]
        assert isinstance(first_row["date"], datetime)
        assert isinstance(first_row["description"], str)
        assert isinstance(first_row["amount"], float)

        # Nubank format doesn't include category, so it should be None
        assert first_row["category"] is None

    def test_nubank_date_parsing(self):
        """Test that Nubank dates are parsed correctly."""
        adapter = AdapterFactory.create_adapter("NUBANK")
        df = adapter.read_invoice("Nubank_2025-10-07.csv")

        # Verify date parsing
        for date in df["date"]:
            assert isinstance(date, datetime)
            assert date.year == 2025


class TestNotionAdapter:
    """Test cases for Notion adapter."""

    def test_convert_to_notion_format(self):
        """Test converting standardized DataFrame to Notion format."""
        # Create sample standardized data
        import pandas as pd

        sample_data = pd.DataFrame(
            [
                {
                    "date": datetime(2025, 10, 1),
                    "description": "Test Transaction",
                    "amount": 100.50,
                    "category": "Food",
                }
            ]
        )

        notion_adapter = NotionAdapter()
        expense_rows = notion_adapter.convert_to_notion_format(
            sample_data, PaymentTypeEnum.CREDIT_CARD
        )

        assert len(expense_rows) == 1

        expense_row = expense_rows[0]
        assert expense_row.date == datetime(2025, 10, 1)
        assert expense_row.description == "Test Transaction"
        assert expense_row.value == 100.50
        assert expense_row.category == "Food"
        assert expense_row.payment == PaymentTypeEnum.CREDIT_CARD.value
        assert expense_row.type_ == "NON-ESSENTIAL"
        assert expense_row.source == "AUTOMATION"

    def test_convert_with_missing_category(self):
        """Test conversion when category is missing."""
        import pandas as pd

        sample_data = pd.DataFrame(
            [
                {
                    "date": datetime(2025, 10, 1),
                    "description": "Test Transaction",
                    "amount": 100.50,
                    "category": None,
                }
            ]
        )

        notion_adapter = NotionAdapter()
        expense_rows = notion_adapter.convert_to_notion_format(sample_data)

        assert expense_rows[0].category == "UNASSIGNED"


class TestIntegration:
    """Integration tests for the complete adapter flow."""

    @pytest.mark.parametrize(
        "bank,file_path",
        [
            ("INTER", "fatura.csv"),
            ("NUBANK", "Nubank_2025-10-07.csv"),
        ],
    )
    def test_complete_adapter_flow(self, bank, file_path):
        """Test complete flow from invoice to Notion format."""
        # Read invoice
        invoice_adapter = AdapterFactory.create_adapter(bank)
        df = invoice_adapter.read_invoice(file_path)

        # Convert to Notion format
        notion_adapter = NotionAdapter()
        expense_rows = notion_adapter.convert_to_notion_format(df)

        # Verify we got expense rows
        assert len(expense_rows) > 0

        # Verify each expense row has required fields
        for expense_row in expense_rows:
            assert hasattr(expense_row, "date")
            assert hasattr(expense_row, "description")
            assert hasattr(expense_row, "value")
            assert hasattr(expense_row, "category")
            assert hasattr(expense_row, "payment")
            assert hasattr(expense_row, "type_")
            assert hasattr(expense_row, "source")
