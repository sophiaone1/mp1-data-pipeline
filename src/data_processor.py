# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    result = df.drop_duplicates()
    logger.debug(f"remove_duplicates: {rows_before} \u2192 {len(result)} rows")
    return result


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis not in ("rows", "columns"):
        logger.error(f"Unsupported axis: {axis}")
        raise ValueError(f"Unsupported axis: {axis}")

    if axis == "rows":
        rows_before = len(df)
        result = df.dropna(axis=0)
        logger.debug(f"handle_missing: {rows_before} \u2192 {len(result)} rows")
    else:
        cols_before = len(df.columns)
        result = df.dropna(axis=1)
        logger.debug(f"handle_missing: {cols_before} \u2192 {len(result.columns)} columns")

    return result


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df.copy()

    for col in columns:
        if col not in result.columns:
            logger.warning(f"Column not found: {col}")
            continue

        if not pd.api.types.is_numeric_dtype(result[col]):
            logger.warning(f"Column is not numeric: {col}")
            continue

        rows_before = len(result)

        if method == "iqr":
            q1 = result[col].quantile(0.25)
            q3 = result[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            result = result[result[col].between(lower, upper)]
            removed = rows_before - len(result)
            logger.debug(f"{col}: lower={lower}, upper={upper}, removed={removed}")
        else:  # zscore
            mean = result[col].mean()
            std = result[col].std()
            z_scores = (result[col] - mean) / std
            result = result[z_scores.abs() <= threshold]
            removed = rows_before - len(result)
            logger.debug(f"{col}: mean={mean}, std={std}, removed={removed}")

    return result


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config.get("processing", {})

    if processing.get("remove_duplicates"):
        df = remove_duplicates(df)

    missing_cfg = processing.get("missing", {})
    if missing_cfg.get("enabled"):
        df = handle_missing(df, axis=missing_cfg.get("axis", "rows"))

    outliers_cfg = processing.get("outliers", {})
    if outliers_cfg.get("enabled"):
        df = remove_outliers(
            df,
            columns=outliers_cfg.get("columns", []),
            method=outliers_cfg.get("method"),
            threshold=outliers_cfg.get("threshold"),
        )

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    return {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns),
    }