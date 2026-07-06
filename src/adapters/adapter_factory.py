from src.enums import BankEnum
from .base_adapter import InvoiceAdapter
from .inter_adapter import InterAdapter
from .nubank_adapter import NubankAdapter


class AdapterFactory:
    """Factory to create the appropriate invoice adapter based on bank type."""

    @staticmethod
    def create_adapter(bank: str) -> InvoiceAdapter:
        """Create the appropriate adapter for the given bank."""
        bank_enum = BankEnum(bank.upper())

        match bank_enum:
            case BankEnum.INTER:
                return InterAdapter()
            case BankEnum.NUBANK:
                return NubankAdapter()
            case _:
                raise ValueError(f"Unsupported bank: {bank}")

    @staticmethod
    def get_supported_banks() -> list[str]:
        """Get list of supported bank names."""
        return [bank.value for bank in BankEnum]
