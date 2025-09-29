import re
import pandas as pd
from enum import StrEnum


class CategoryEnum(StrEnum):
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
            "AMAZON": CategoryEnum.AMAZON,
            "CAMARIM": CategoryEnum.BEAUTY,
            "RAIADROGASIL": CategoryEnum.HEALTH,
            "DROGASIL": CategoryEnum.HEALTH,
            "99 RIDE": CategoryEnum.TRANSPORT,
            "UBER": CategoryEnum.TRANSPORT,
            "IFOOD": CategoryEnum.FOOD,
            "IFD": CategoryEnum.FOOD,
            "MERCAD": CategoryEnum.SUPERMARKET,
            "CARREFOUR": CategoryEnum.SUPERMARKET,
            "SONYPLAYSTATN": CategoryEnum.GAMES,
            "PLAYSTATION": CategoryEnum.GAMES,
            "HBOMAX": CategoryEnum.SUBSCRIPTION,
            "NETFLIX": CategoryEnum.SUBSCRIPTION,
            "SPOTIFY": CategoryEnum.SUBSCRIPTION,
            "GOOGLE ONE": CategoryEnum.SUBSCRIPTION,
            "BRISANET": CategoryEnum.HOME,
            "CONTA VIVO": CategoryEnum.HOME,
            "DELL": CategoryEnum.ELETRONIC,
            "YOUTUBE": CategoryEnum.SUBSCRIPTION,
            # Categorias genéricas vindas do extrato
            "RESTAURANTES": CategoryEnum.FOOD,
            "SUPERMERCADO": CategoryEnum.SUPERMARKET,
            "DROGARIA": CategoryEnum.HEALTH,
            "TRANSPORTE": CategoryEnum.TRANSPORT,
            "ENTRETENIMENTO": CategoryEnum.LEISURE,
            "PAGAMENTOS": CategoryEnum.SERVICE,
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
    ) -> pd.DataFrame:
        df[target_column] = df.apply(
            lambda row: self._map_if_none(row, source_column, target_column),
            axis=1,
        )
        return df

    def _map_if_none(
        self,
        row,
        source_column: str,
        target_column: str,
    ) -> str:
        current_value = row.get(target_column)
        if pd.isna(current_value) or current_value is None:
            mapped = self.map_category(str(row[source_column]))
            return mapped
        return current_value
