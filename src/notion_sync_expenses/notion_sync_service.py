import pandas as pd

from src.enums import PaymentTypeEnum
from src.envs import FINANCE_DASHBOARD_ID, MONTHLY_INVOICE_FILENAME
from src.notion_gateway import NotionAPIGateway, ExpenseRow
from src.notion_sync_expenses.category_mapper import CategoryEnum, CategoryMapper


class NotionSyncService:
    def __init__(self):
        self.gateway = NotionAPIGateway()
        self.category_mapper = CategoryMapper()

    def sync_expenses(self) -> None:
        monthly_invoice_df = pd.read_csv(MONTHLY_INVOICE_FILENAME, sep=",")

        df = self.category_mapper.map_dataframe(
            df=monthly_invoice_df,
            source_column="Lançamento",
            target_column="NewCategory",
        )
        df = self.category_mapper.map_dataframe(
            df=df,
            source_column="Categoria",
            target_column="NewCategory",
        )

        df["NewCategory"] = df["NewCategory"].fillna(CategoryEnum.UNASSIGNED)
        df["Categoria"] = df["NewCategory"]

        payloads = [
            NotionAPIGateway.build_payload(
                database_id=FINANCE_DASHBOARD_ID,
                expense=ExpenseRow.from_series(
                    row, payment_type=PaymentTypeEnum.CREDIT_CARD
                ),
            )
            for _, row in df.iterrows()
        ]

        self.gateway.send_payloads(payloads)
