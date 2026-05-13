"""Data loading and summary utilities for reports."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load CSV or Excel file into a cleaned pandas DataFrame.

    Supported input formats are: .csv, .xlsx, .xls.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)
    elif extension in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(
            f"Unsupported file type '{extension}'. Supported types: .csv, .xlsx, .xls"
        )

    df.columns = [str(col).strip() for col in df.columns]
    df = df.dropna(how="all")
    return df


def get_summary_stats(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a summary dictionary for a DataFrame.

    Includes counts, column names, and min/max/mean/sum for numeric columns.
    """
    numeric_df = df.select_dtypes(include="number")
    numeric_summary: dict[str, dict[str, float]] = {}

    for column in numeric_df.columns:
        series = numeric_df[column].dropna()
        if series.empty:
            continue
        numeric_summary[str(column)] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "sum": float(series.sum()),
        }

    return {
        "row_count": int(df.shape[0]),
        "col_count": int(df.shape[1]),
        "columns": [str(col) for col in df.columns],
        "numeric_summary": numeric_summary,
    }
