# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    result = df.drop_duplicates()
    logger.debug(f"remove_duplicates: {rows_before} → {len(result)} rows")
    return result


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis not in ("rows", "columns"):
        logger.error(f"Unsupported axis: {axis}")
        raise ValueError(f"Unsupported axis: {axis}")

    if axis == "rows":
        rows_before = len(df)
        result = df.dropna(axis=0)
        logger.debug(f"handle_missing: {rows_before} → {len(result)} rows")
    else:
        cols_before = len(df.columns)
        result = df.dropna(axis=1)
        logger.debug(f"handle_missing: {cols_before} → {len(result.columns)} columns")

    return result


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df.copy()

    for col in columns:
        if col not in result.columns:
        