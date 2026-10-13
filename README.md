# MP1 Data Pipeline

This project is a configurable command-line data pipeline built for DS 3500. It loads a dataset, validates it against a set of rules, cleans it, and saves the result — all driven by a single YAML configuration file rather than hard-coded logic. The pipeline currently supports CSV, JSON, and YAML inputs and can be pointed at any compatible CSV file simply by updating the command-line arguments and the relevant column names in the config.

Data moves through the pipeline in four stages: it is loaded by `src/data_loaders.py` (which picks the right loader based on file extension), validated by `src/data_validator.py` (checking required columns exist and coercing numeric columns, dropping any unconvertible values), cleaned by `src/data_processor.py` (removing duplicates, handling missing values, and stripping outliers using the IQR method), and finally written to disk by `src/data_output.py`. `pipeline.py` at the project root coordinates all four stages and handles argument parsing, logging setup, and error handling via `src/utils.py`.

Each module has a single responsibility: `data_loaders.py` only reads files, `data_validator.py` only checks and coerces data, `data_processor.py` only applies the configured cleaning steps, `data_output.py` only writes files, and `utils.py` holds shared logging and file-validation helpers. This separation means new processing or validation rules can be added without touching the loading or saving logic, and the pipeline's behavior for any given dataset is controlled entirely through `config/config.yaml`.

## Running the pipeline

```bash
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

Example output:

```
23:26:12 INFO     __main__ — Input file validated: fixtures/sample_data.csv
23:26:12 INFO     __main__ — Input file validated: config/config.yaml
23:26:12 INFO     src.data_loaders — Loaded CSV file: fixtures/sample_data.csv (100 rows)
23:26:12 INFO     src.data_loaders — Loaded YAML file: config/config.yaml
23:26:12 WARNING  src.data_validator — Removed 2 rows with invalid numeric values in rating
23:26:12 DEBUG    src.data_validator — Validation: 100 → 98 rows
23:26:12 INFO     __main__ — Validation complete: 100 → 98 rows
23:26:12 DEBUG    src.data_processor — remove_duplicates: 98 → 96 rows
23:26:12 DEBUG    src.data_processor — handle_missing: 96 → 94 rows
23:26:12 DEBUG    src.data_processor — rating: method=iqr, threshold=1.5, removed=2
23:26:12 INFO     __main__ — Processing complete: 98 → 92 rows
23:26:12 DEBUG    src.data_output — Saved 92 rows to output/clean.csv
23:26:12 INFO     __main__ — Saved cleaned data to output/clean.csv
{'rows_before': 98, 'rows_after': 92, 'rows_removed': 6, 'columns_before': 5, 'columns_after': 5, 'columns_removed': 0}
```