# src/data_validator.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be
    numeric.
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        logger.error(f"Missing required columns: {missing}")
        raise ValueError(f"Missing required columns: {missing}")

    rows_before = len(df)
    result = df.copy()

    for col in numeric_columns:
        invalid_rows = []
        for i, value in result[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    invalid_rows.append(i)

        if invalid_rows:
            logger.warning(
                f"Removed {len(invalid_rows)} rows with invalid numeric values in {col}"
            )
            result = result.drop(index=invalid_rows)

        # convert to a numeric data type
        result[col] = pd.to_numeric(result[col])

    rows_after = len(result)
    logger.debug(f"Validation: {rows_before} → {rows_after} rows")

    return result
