from enum import StrEnum


class PaymentTypeEnum(StrEnum):
    CREDIT_CARD = "CREDIT_CARD"
    PIX = "PIX"


class BankEnum(StrEnum):
    NUBANK = "NUBANK"
    INTER = "INTER"
