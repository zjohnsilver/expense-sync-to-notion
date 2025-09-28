import re
import pandas as pd
from enum import StrEnum


class Category(StrEnum):
    AMAZON = "Amazon"
    BEAUTY = "Beauty"
    HEALTH = "Health"
    TRANSPORT = "Transport"
    FOOD = "Food"
    GAMES = "Games"
    SUBSCRIPTION = "Subscription"
    SUPERMARKET = "Supermarket"
    LEISURE = "Leisure"
    SERVICE = "Service"
    HOME = "Home"
    ELETRONIC = "Electronic"
    UNASSIGNED = "UNASSIGNED"


class CategoryMapper:
    def __init__(self) -> None:
        self.rules = {
            # Mapeamento direto pelo lançamento
            "AMAZON": Category.AMAZON,
            "CAMARIM": Category.BEAUTY,
            "RAIADROGASIL": Category.HEALTH,
            "DROGASIL": Category.HEALTH,
            "99 RIDE": Category.TRANSPORT,
            "UBER": Category.TRANSPORT,
            "IFOOD": Category.FOOD,
            "IFD": Category.FOOD,
            "MERCAD": Category.SUPERMARKET,
            "CARREFOUR": Category.SUPERMARKET,
            "SONYPLAYSTATN": Category.GAMES,
            "PLAYSTATION": Category.GAMES,
            "HBOMAX": Category.SUBSCRIPTION,
            "NETFLIX": Category.SUBSCRIPTION,
            "SPOTIFY": Category.SUBSCRIPTION,
            "GOOGLE ONE": Category.SUBSCRIPTION,
            "BRISANET": Category.HOME,
            "CONTA VIVO": Category.HOME,
            "DELL": Category.ELETRONIC,
            "YOUTUBE": Category.SUBSCRIPTION,
            # Categorias genéricas vindas do extrato
            "RESTAURANTES": Category.FOOD,
            "SUPERMERCADO": Category.SUPERMARKET,
            "DROGARIA": Category.HEALTH,
            "TRANSPORTE": Category.TRANSPORT,
            "ENTRETENIMENTO": Category.LEISURE,
            "PAGAMENTOS": Category.SERVICE,
        }

    def add_rule(self, pattern: str, category: str) -> None:
        self.rules[pattern] = category

    def map_category(self, description: str) -> str | None:
        if not description:
            return None

        text = description.upper()
        for pattern, category in self.rules.items():
            if re.search(pattern, text, re.IGNORECASE):
                return category
        return None

    def map_dataframe(
        self,
        df: pd.DataFrame,
        source_column: str,
        target_column: str,
        allow_unassigned: bool = False,
    ) -> pd.DataFrame:
        df[target_column] = df.apply(
            lambda row: self._map_if_none(
                row, source_column, target_column, allow_unassigned
            ),
            axis=1,
        )
        return df

    def _map_if_none(
        self,
        row,
        source_column: str,
        target_column: str,
        allow_unassigned: bool = False,
    ) -> str:
        current_value = row.get(target_column)
        if pd.isna(current_value) or current_value is None:
            mapped = self.map_category(str(row[source_column]))
            if mapped is None and allow_unassigned:
                return Category.UNASSIGNED
            return mapped
        return current_value
