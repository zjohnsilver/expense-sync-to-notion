from src.adapters.adapter_factory import AdapterFactory
from src.adapters.notion_adapter import NotionAdapter
from src.enums import PaymentTypeEnum
from src.envs import FINANCE_DASHBOARD_ID, MONTHLY_INVOICE_FILENAME, INVOICE_BANK
from src.notion_gateway import NotionAPIGateway
from src.notion_sync_expenses.category_mapper import CategoryEnum, CategoryMapper


class NotionSyncService:
    def __init__(self):
        self.gateway = NotionAPIGateway()
        self.category_mapper = CategoryMapper()
        self.invoice_adapter = AdapterFactory.create_adapter("INTER")
        self.notion_adapter = NotionAdapter()

    def sync_expenses(self) -> None:
        standardized_df = self.invoice_adapter.read_invoice("fatura.csv")

        # TODO: adapt category from column description or category.

        df = self.category_mapper.map_dataframe(
            df=standardized_df,
            source_column="description",
            target_column="category",
        )

        df["category"] = df["category"].fillna(CategoryEnum.UNASSIGNED)

        expense_rows = self.notion_adapter.convert_to_notion_format(
            df, payment_type=PaymentTypeEnum.CREDIT_CARD
        )

        payloads = [
            NotionAPIGateway.build_payload(
                database_id=FINANCE_DASHBOARD_ID,
                expense=expense_row,
            )
            for expense_row in expense_rows
        ]

        for payload in payloads:
            print(payload)
            print("-" * 200)

        # self.gateway.send_payloads(payloads)
