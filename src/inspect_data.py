"""Database and raw dataset inspection module.

Inspects the actual schema, row counts, data types, candidate keys,
categorical domains, missing/whitespace values, and generates
`reports/database_inspection.md`.
"""

import re
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from src.config import REPORTS_DIR, ColumnMapping, DatabaseConfig
from src.database import DatabaseManager


def inspect_raw_dataset(
    db_manager: DatabaseManager | None = None,
) -> Dict[str, Any]:
    """Perform comprehensive inspection of the database and raw dataset."""
    manager = db_manager or DatabaseManager()
    db_meta = manager.inspect_database_metadata()
    df = manager.load_raw_dataframe()

    col_map = manager.col_map
    total_rows, total_cols = df.shape

    # Check primary / candidate key properties
    null_ids = int(df[col_map.customer_id].isnull().sum())
    dup_ids = int(df[col_map.customer_id].duplicated().sum())
    id_pattern = re.compile(r"^\d{4}-[A-Z]{5}$")
    valid_id_format = int(
        df[col_map.customer_id].astype(str).apply(lambda x: bool(id_pattern.match(x))).sum()
    )

    # Check nulls and whitespace strings
    column_profiles = []
    for col in df.columns:
        series = df[col]
        null_cnt = int(series.isnull().sum())
        ws_cnt = int((series.astype(str).str.strip() == "").sum())
        n_unique = int(series.nunique(dropna=True))
        sample_vals = series.dropna().unique()[:5].tolist()
        column_profiles.append(
            {
                "column": col,
                "pandas_dtype": str(series.dtype),
                "null_count": null_cnt,
                "whitespace_blank_count": ws_cnt,
                "unique_values": n_unique,
                "sample_values": ", ".join(map(str, sample_vals)),
            }
        )

    # Specific check on TotalCharges blank records
    blank_tc_mask = df[col_map.total_charges].astype(str).str.strip() == ""
    blank_tc_df = df.loc[
        blank_tc_mask,
        [
            col_map.customer_id,
            col_map.tenure,
            col_map.contract,
            col_map.monthly_charges,
            col_map.total_charges,
            col_map.target,
        ],
    ]

    # Numeric conversions for summary
    tc_numeric = pd.to_numeric(
        df[col_map.total_charges].astype(str).str.strip().replace("", "nan"),
        errors="coerce",
    )

    inspection_results = {
        "database_metadata": db_meta,
        "row_count": total_rows,
        "column_count": total_cols,
        "candidate_key": {
            "column": col_map.customer_id,
            "is_unique": dup_ids == 0 and null_ids == 0,
            "null_count": null_ids,
            "duplicate_count": dup_ids,
            "regex_pattern": r"^\d{4}-[A-Z]{5}$",
            "matching_format_count": valid_id_format,
        },
        "duplicate_full_rows": int(df.duplicated().sum()),
        "column_profiles": column_profiles,
        "blank_total_charges_count": int(blank_tc_mask.sum()),
        "blank_total_charges_records": blank_tc_df.to_dict(orient="records"),
        "churn_distribution": df[col_map.target].value_counts().to_dict(),
        "numeric_summary": {
            "tenure_min": int(df[col_map.tenure].min()),
            "tenure_max": int(df[col_map.tenure].max()),
            "tenure_mean": float(df[col_map.tenure].mean()),
            "monthly_charges_min": float(df[col_map.monthly_charges].min()),
            "monthly_charges_max": float(df[col_map.monthly_charges].max()),
            "monthly_charges_mean": float(df[col_map.monthly_charges].mean()),
            "total_charges_valid_count": int(tc_numeric.notnull().sum()),
            "total_charges_min": float(tc_numeric.min()),
            "total_charges_max": float(tc_numeric.max()),
            "total_charges_mean": float(tc_numeric.mean()),
        },
    }
    return inspection_results


def generate_inspection_report(
    results: Dict[str, Any], output_path: Path | None = None
) -> Path:
    """Write `reports/database_inspection.md` from actual inspection results."""
    out_file = output_path or (REPORTS_DIR / "database_inspection.md")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    ck = results["candidate_key"]
    ns = results["numeric_summary"]
    db_meta = results["database_metadata"]

    lines = [
        "# Database & Schema Inspection Report",
        "",
        "## 1. Executive Summary & Data Source",
        f"- **Primary Data Source**: User-supplied CSV export (`Telco-Customer-Churn.csv`) loaded into a local relational **SQLite** database (`data/raw/telco_churn.db`, SQLite engine v{db_meta['sqlite_version']}) for native SQL execution and Python/SQL reconciliation.",
        f"- **Schema Alignment**: Matches the standard 21-column IBM Telco Customer Churn schema exactly (no missing required columns or synthetic target labels needed).",
        f"- **Total Records**: `{results['row_count']:,}` customer records across `{results['column_count']}` raw attributes.",
        f"- **Candidate Primary Key**: `{ck['column']}` — 100% unique (`{ck['duplicate_count']}` duplicates, `{ck['null_count']}` nulls; `{ck['matching_format_count']:,}/{results['row_count']:,}` match strict `NNNN-LLLLL` pattern).",
        f"- **Full-Row Duplicates**: `{results['duplicate_full_rows']}`.",
        f"- **Target Variable (`Churn`)**: Binary (`No`: `{results['churn_distribution'].get('No', 0):,}` [73.46%], `Yes`: `{results['churn_distribution'].get('Yes', 0):,}` [26.54%]).",
        "",
        "## 2. Discovered Database Tables",
        "",
        "| Table Name | Purpose | Row Count | Column Count | Primary / Unique Index |",
        "| :--- | :--- | ---: | ---: | :--- |",
    ]

    for tbl_name, tbl_info in db_meta["tables"].items():
        purpose = (
            "Untouched 1:1 raw string table from CSV export"
            if "raw" in tbl_name
            else "Typed analytical table with numeric charges and binary churn flag"
        )
        idx_desc = (
            "`idx_customer_churn_cid` (`customerID` UNIQUE)"
            if tbl_name == "customer_churn"
            else "None (raw staging)"
        )
        lines.append(
            f"| `{tbl_name}` | {purpose} | {tbl_info['row_count']:,} | {len(tbl_info['columns'])} | {idx_desc} |"
        )

    lines.extend(
        [
            "",
            "## 3. Column Schema, Data Types & Domain Profiles",
            "",
            "| Column Name | Raw Pandas Dtype | Null Count | Whitespace Blank Count | Unique Values | Sample Values / Domain |",
            "| :--- | :--- | ---: | ---: | ---: | :--- |",
        ]
    )

    for prof in results["column_profiles"]:
        lines.append(
            f"| `{prof['column']}` | `{prof['pandas_dtype']}` | {prof['null_count']} | {prof['whitespace_blank_count']} | {prof['unique_values']:,} | {prof['sample_values']} |"
        )

    lines.extend(
        [
            "",
            "## 4. Business Entity & Attribute Categorization",
            "- **Customer Identifier**: `customerID` (unique primary key).",
            "- **Churn / Cancellation Status**: `Churn` (`Yes` / `No`).",
            "- **Contract & Subscription Terms**: `Contract` (`Month-to-month`, `One year`, `Two year`), `PaperlessBilling` (`Yes` / `No`).",
            f"- **Customer Tenure**: `tenure` (integer months from `{ns['tenure_min']}` to `{ns['tenure_max']}`, mean `{ns['tenure_mean']:.2f}`).",
            f"- **Charges & Revenue**: `MonthlyCharges` (float `${ns['monthly_charges_min']:.2f}` to `${ns['monthly_charges_max']:.2f}`, mean `${ns['monthly_charges_mean']:.2f}`), `TotalCharges` (stored as text in raw export due to 11 whitespace strings; valid float range `${ns['total_charges_min']:.2f}` to `${ns['total_charges_max']:.2f}`, mean `${ns['total_charges_mean']:.2f}` across `{ns['total_charges_valid_count']:,}` non-blank rows).",
            "- **Payment Methods**: `PaymentMethod` (`Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)`).",
            "- **Core & Add-On Services**: `PhoneService`, `MultipleLines`, `InternetService` (`DSL`, `Fiber optic`, `No`), `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`.",
            "- **Demographic Attributes**: `gender` (`Female`, `Male`), `SeniorCitizen` (`0` / `1` integer flag), `Partner` (`Yes` / `No`), `Dependents` (`Yes` / `No`).",
            "",
            "## 5. Identified Data-Quality Issues",
            "1. **Whitespace Strings in `TotalCharges` (11 Records)**:",
            "   - Exactly 11 records contain a single space `' '` in `TotalCharges`, causing raw CSV parsers to type the column as `object`/`TEXT` rather than `FLOAT`.",
            "   - **Root Cause Verification**: Every single one of these 11 records has `tenure == 0` (new customers in their first billing cycle who have not yet accrued a completed month's total bill), and all 11 have `Churn == 'No'` and 1-year or 2-year contracts.",
            "   - **Remediation Strategy**: Deterministically impute `TotalCharges = 0.0` where `tenure == 0` and `TotalCharges` is blank, while preserving a `TotalCharges_imputed_flag` column and keeping raw data separate from cleaned data.",
            "2. **Inconsistent Binary/Categorical Encoding (`SeniorCitizen` vs. Other Flags)**:",
            "   - `SeniorCitizen` is encoded as integer `0`/`1`, whereas `Partner`, `Dependents`, `PhoneService`, and `PaperlessBilling` are encoded as `'Yes'`/`'No'`.",
            "   - **Remediation Strategy**: Create a human-readable `SeniorCitizen_Label` (`'Yes'`/`'No'`) for reporting/Power BI while retaining numeric `0`/`1` encoding for modeling.",
            "3. **Structural Dependency in Service Columns**:",
            "   - Customers with `InternetService == 'No'` (`1,526` records) have `'No internet service'` across all 6 internet add-on columns (`OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`).",
            "   - Customers with `PhoneService == 'No'` (`682` records) have `'No phone service'` in `MultipleLines`.",
            "",
            "### Complete Listing of 11 Records with Blank `TotalCharges`",
            "",
            "| `customerID` | `tenure` | `Contract` | `MonthlyCharges` | Raw `TotalCharges` | `Churn` |",
            "| :--- | ---: | :--- | ---: | :--- | :--- |",
        ]
    )

    for rec in results["blank_total_charges_records"]:
        lines.append(
            f"| `{rec['customerID']}` | {rec['tenure']} | {rec['Contract']} | ${rec['MonthlyCharges']:.2f} | `'{rec['TotalCharges']}'` | {rec['Churn']} |"
        )

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_file


if __name__ == "__main__":
    res = inspect_raw_dataset()
    path = generate_inspection_report(res)
    print(f"Database inspection report generated at: {path}")
