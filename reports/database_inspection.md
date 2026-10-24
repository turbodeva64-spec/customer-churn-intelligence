# Database & Schema Inspection Report

## 1. Executive Summary & Data Source
- **Primary Data Source**: User-supplied CSV export (`Telco-Customer-Churn.csv`) loaded into a local relational **SQLite** database (`data/raw/telco_churn.db`, SQLite engine v3.40.1) for native SQL execution and Python/SQL reconciliation.
- **Schema Alignment**: Matches the standard 21-column IBM Telco Customer Churn schema exactly (no missing required columns or synthetic target labels needed).
- **Total Records**: `7,043` customer records across `21` raw attributes.
- **Candidate Primary Key**: `customerID` — 100% unique (`0` duplicates, `0` nulls; `7,043/7,043` match strict `NNNN-LLLLL` pattern).
- **Full-Row Duplicates**: `0`.
- **Target Variable (`Churn`)**: Binary (`No`: `5,174` [73.46%], `Yes`: `1,869` [26.54%]).

## 2. Discovered Database Tables

| Table Name | Purpose | Row Count | Column Count | Primary / Unique Index |
| :--- | :--- | ---: | ---: | :--- |
| `customer_churn` | Typed analytical table with numeric charges and binary churn flag | 7,043 | 23 | `idx_customer_churn_cid` (`customerID` UNIQUE) |
| `customer_churn_raw` | Untouched 1:1 raw string table from CSV export | 7,043 | 21 | None (raw staging) |

## 3. Column Schema, Data Types & Domain Profiles

| Column Name | Raw Pandas Dtype | Null Count | Whitespace Blank Count | Unique Values | Sample Values / Domain |
| :--- | :--- | ---: | ---: | ---: | :--- |
| `customerID` | `object` | 0 | 0 | 7,043 | 7590-VHVEG, 5575-GNVDE, 3668-QPYBK, 7795-CFOCW, 9237-HQITU |
| `gender` | `object` | 0 | 0 | 2 | Female, Male |
| `SeniorCitizen` | `int64` | 0 | 0 | 2 | 0, 1 |
| `Partner` | `object` | 0 | 0 | 2 | Yes, No |
| `Dependents` | `object` | 0 | 0 | 2 | No, Yes |
| `tenure` | `int64` | 0 | 0 | 73 | 1, 34, 2, 45, 8 |
| `PhoneService` | `object` | 0 | 0 | 2 | No, Yes |
| `MultipleLines` | `object` | 0 | 0 | 3 | No phone service, No, Yes |
| `InternetService` | `object` | 0 | 0 | 3 | DSL, Fiber optic, No |
| `OnlineSecurity` | `object` | 0 | 0 | 3 | No, Yes, No internet service |
| `OnlineBackup` | `object` | 0 | 0 | 3 | Yes, No, No internet service |
| `DeviceProtection` | `object` | 0 | 0 | 3 | No, Yes, No internet service |
| `TechSupport` | `object` | 0 | 0 | 3 | No, Yes, No internet service |
| `StreamingTV` | `object` | 0 | 0 | 3 | No, Yes, No internet service |
| `StreamingMovies` | `object` | 0 | 0 | 3 | No, Yes, No internet service |
| `Contract` | `object` | 0 | 0 | 3 | Month-to-month, One year, Two year |
| `PaperlessBilling` | `object` | 0 | 0 | 2 | Yes, No |
| `PaymentMethod` | `object` | 0 | 0 | 4 | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) |
| `MonthlyCharges` | `float64` | 0 | 0 | 1,585 | 29.85, 56.95, 53.85, 42.3, 70.7 |
| `TotalCharges` | `object` | 0 | 11 | 6,531 | 29.85, 1889.5, 108.15, 1840.75, 151.65 |
| `Churn` | `object` | 0 | 0 | 2 | No, Yes |

## 4. Business Entity & Attribute Categorization
- **Customer Identifier**: `customerID` (unique primary key).
- **Churn / Cancellation Status**: `Churn` (`Yes` / `No`).
- **Contract & Subscription Terms**: `Contract` (`Month-to-month`, `One year`, `Two year`), `PaperlessBilling` (`Yes` / `No`).
- **Customer Tenure**: `tenure` (integer months from `0` to `72`, mean `32.37`).
- **Charges & Revenue**: `MonthlyCharges` (float `$18.25` to `$118.75`, mean `$64.76`), `TotalCharges` (stored as text in raw export due to 11 whitespace strings; valid float range `$18.80` to `$8684.80`, mean `$2283.30` across `7,032` non-blank rows).
- **Payment Methods**: `PaymentMethod` (`Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)`).
- **Core & Add-On Services**: `PhoneService`, `MultipleLines`, `InternetService` (`DSL`, `Fiber optic`, `No`), `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`.
- **Demographic Attributes**: `gender` (`Female`, `Male`), `SeniorCitizen` (`0` / `1` integer flag), `Partner` (`Yes` / `No`), `Dependents` (`Yes` / `No`).

## 5. Identified Data-Quality Issues
1. **Whitespace Strings in `TotalCharges` (11 Records)**:
   - Exactly 11 records contain a single space `' '` in `TotalCharges`, causing raw CSV parsers to type the column as `object`/`TEXT` rather than `FLOAT`.
   - **Root Cause Verification**: Every single one of these 11 records has `tenure == 0` (new customers in their first billing cycle who have not yet accrued a completed month's total bill), and all 11 have `Churn == 'No'` and 1-year or 2-year contracts.
   - **Remediation Strategy**: Deterministically impute `TotalCharges = 0.0` where `tenure == 0` and `TotalCharges` is blank, while preserving a `TotalCharges_imputed_flag` column and keeping raw data separate from cleaned data.
2. **Inconsistent Binary/Categorical Encoding (`SeniorCitizen` vs. Other Flags)**:
   - `SeniorCitizen` is encoded as integer `0`/`1`, whereas `Partner`, `Dependents`, `PhoneService`, and `PaperlessBilling` are encoded as `'Yes'`/`'No'`.
   - **Remediation Strategy**: Create a human-readable `SeniorCitizen_Label` (`'Yes'`/`'No'`) for reporting/Power BI while retaining numeric `0`/`1` encoding for modeling.
3. **Structural Dependency in Service Columns**:
   - Customers with `InternetService == 'No'` (`1,526` records) have `'No internet service'` across all 6 internet add-on columns (`OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`).
   - Customers with `PhoneService == 'No'` (`682` records) have `'No phone service'` in `MultipleLines`.

### Complete Listing of 11 Records with Blank `TotalCharges`

| `customerID` | `tenure` | `Contract` | `MonthlyCharges` | Raw `TotalCharges` | `Churn` |
| :--- | ---: | :--- | ---: | :--- | :--- |
| `4472-LVYGI` | 0 | Two year | $52.55 | `' '` | No |
| `3115-CZMZD` | 0 | Two year | $20.25 | `' '` | No |
| `5709-LVOEQ` | 0 | Two year | $80.85 | `' '` | No |
| `4367-NUYAO` | 0 | Two year | $25.75 | `' '` | No |
| `1371-DWPAZ` | 0 | Two year | $56.05 | `' '` | No |
| `7644-OMVMY` | 0 | Two year | $19.85 | `' '` | No |
| `3213-VVOLG` | 0 | Two year | $25.35 | `' '` | No |
| `2520-SGTTA` | 0 | Two year | $20.00 | `' '` | No |
| `2923-ARZLG` | 0 | One year | $19.70 | `' '` | No |
| `4075-WKNIU` | 0 | Two year | $73.35 | `' '` | No |
| `2775-SEFEE` | 0 | Two year | $61.90 | `' '` | No |
