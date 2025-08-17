import re
import unicodedata
from io import BytesIO, StringIO
from typing import Literal

import pandas as pd

FileType = Literal["CREDIT_CARD_INVOICE", "BANK_ACCOUNT_STATEMENT"]


def parse_uploaded_file(file_obj, file_type: FileType) -> pd.DataFrame:
    """Parse an uploaded CSV into a normalized DataFrame with columns:
    - Data (DD/MM/YYYY)
    - Lançamento (string)
    - Categoria (string)
    - Valor (string or number string with comma as decimal)

    The bank statement format from Inter contains preamble lines and uses ';' as a separator.
    """
    if file_type == "BANK_ACCOUNT_STATEMENT":
        return _parse_bank_account_statement(file_obj)
    else:
        return _parse_credit_card_invoice(file_obj)


def _parse_credit_card_invoice(file_obj) -> pd.DataFrame:
    # Assume already in expected format with comma separator
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    df = pd.read_csv(file_obj, sep=",")
    # Ensure required columns exist; create defaults if missing
    if "Categoria" not in df.columns:
        df["Categoria"] = "UNASSIGNED"
    # Normalize whitespace in key columns
    for col in ["Data", "Lançamento", "Categoria", "Valor"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df[
        [c for c in ["Data", "Lançamento", "Categoria", "Valor"] if c in df.columns]
    ]


def _parse_bank_account_statement(file_obj) -> pd.DataFrame:
    # Read whole content and detect the header line robustly
    file_bytes: bytes
    if hasattr(file_obj, "getvalue"):
        file_bytes = file_obj.getvalue()
    else:
        # Fall back to read(); do not rely on seek/rewind
        file_bytes = file_obj.read()

    text = file_bytes.decode("utf-8-sig", errors="ignore")
    lines = text.splitlines()

    def _norm(s: str) -> str:
        s = s.replace("\ufeff", "")
        s = unicodedata.normalize("NFKD", s)
        s = s.encode("ASCII", "ignore").decode("ASCII")
        s = re.sub(r"\s+", " ", s).strip().lower()
        return s

    header_idx = None
    for i, line in enumerate(lines):
        n = _norm(line)
        # Look for a line that looks like the header with semicolon-separated labels
        if (
            ("data" in n and "valor" in n)
            and ("lancamento" in n or "historico" in n or "descricao" in n)
            and (";" in line)
        ):
            header_idx = i
            break

    if header_idx is None:
        # Fallback: try the 6th line (0-based 5) if available, else first line
        header_idx = 5 if len(lines) > 5 else 0

    sliced_text = "\n".join(lines[header_idx:])
    buffer = StringIO(sliced_text)
    df = pd.read_csv(buffer, sep=";", header=0, dtype=str)

    # Normalize column names: strip, collapse whitespace, remove BOM/diacritics for matching
    def _normalize_header_name(name: str) -> str:
        if name is None:
            return ""
        # Remove BOM and normalize unicode
        name = str(name).replace("\ufeff", "")
        name = unicodedata.normalize("NFKD", name)
        name = name.encode("ASCII", "ignore").decode("ASCII")
        name = re.sub(r"\s+", " ", name).strip().lower()
        return name

    original_columns = list(df.columns)
    normalized_map = {_normalize_header_name(c): c for c in original_columns}

    # Helper to fetch column by canonical name
    def _col(canonical: str) -> str:
        key = _normalize_header_name(canonical)
        if key in normalized_map:
            return normalized_map[key]
        # Try partial contains match
        for k, v in normalized_map.items():
            if key in k:
                return v
        raise KeyError(canonical)

    # Keep only expected columns if present
    expected_cols = ["Data Lançamento", "Histórico", "Descrição", "Valor", "Saldo"]
    available_cols = []
    for c in expected_cols:
        try:
            available_cols.append(_col(c))
        except KeyError:
            continue
    if not available_cols:
        # If nothing matched, raise with diagnostic
        raise KeyError(f"None of expected columns found. Got: {original_columns}")
    df = df[available_cols].copy()

    # Normalize strings and fill NaNs
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Build normalized columns
    df_normalized = pd.DataFrame()
    df_normalized["Data"] = df[_col("Data Lançamento")].astype(str).str.strip()

    # Combine Histórico and Descrição for Lançamento
    historico = df.get(_col("Histórico"), pd.Series([""] * len(df)))
    descricao = df.get(_col("Descrição"), pd.Series([""] * len(df)))
    lancamento = historico.fillna("").astype(str).str.strip()
    desc = descricao.fillna("").astype(str).str.strip()
    combined = (lancamento + " - " + desc).str.replace(r"\s+-\s+$", "", regex=True)
    df_normalized["Lançamento"] = combined.str.strip()

    # Categoria default to UNASSIGNED (user can edit later)
    df_normalized["Categoria"] = "UNASSIGNED"

    # Valor as is (may include negative sign and comma decimal). Keep string; conversion later
    df_normalized["Valor"] = df[_col("Valor")].astype(str).str.strip()

    # Drop rows without date or value
    df_normalized = df_normalized[
        (df_normalized["Data"].notna()) & (df_normalized["Data"] != "nan")
    ]

    # Reset index to ensure line numbers align with display (1-based later)
    df_normalized = df_normalized.reset_index(drop=True)

    return df_normalized
