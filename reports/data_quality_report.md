# Data Quality & Cleaning Report

## 1. Cleaning Pipeline Audit Summary
- **Raw Input Records**: `7,043`
- **Cleaned Output Records**: `7,043` (Zero customer records dropped)
- **Duplicate Customer IDs Removed**: `0`
- **Blank `TotalCharges` Detected**: `11`
- **Blank `TotalCharges` Explained by `tenure == 0`**: `11` (`100.0%` of blank cases)
- **Remaining Null Values Across All Columns**: `0`
- **Validated Target Balance**: `1,869` Churned (`26.54%`) vs. `5,174` Retained (`73.46%`)

## 2. Investigation & Handling of Missing `TotalCharges`
Before applying any transformation, all 11 records with whitespace-only `TotalCharges` were inspected:
- Every affected record had `tenure == 0`, indicating a newly onboarded customer on a 1-year or 2-year contract who had not yet completed their first billing cycle.
- Dropping these 11 rows would bias the tenure=0 cohort and discard valid active customers; imputing with the global mean/median (`$2,283.30` / `$1,397.48`) would introduce severe accounting distortion for brand-new customers.
- **Implemented Solution**: Set `TotalCharges = 0.0` where `tenure == 0` and flagged those 11 rows via `TotalCharges_Imputed_Flag = 1` for full auditability.

## 3. Raw vs. Processed Data Separation
- **Raw Source**: Untouched in `user_uploaded_files/.../Telco-Customer-Churn.csv` and staged 1:1 in SQLite table `customer_churn_raw`.
- **Processed Output**: Exported to `data/processed/cleaned_churn.csv` (`7,043` rows, `29` columns) and indexed in SQLite table `customer_churn`.

## 4. Complete Data Dictionary (`data/processed/data_dictionary.csv`)

| Column Name | Data Type | Null Count | Unique Values | Description |
| :--- | :--- | ---: | ---: | :--- |
| `customerID` | `object` | 0 | 7,043 | Unique alphanumeric customer identifier (Primary Key, format NNNN-LLLLL) |
| `gender` | `object` | 0 | 2 | Customer gender ('Female', 'Male') |
| `SeniorCitizen` | `int64` | 0 | 2 | Binary indicator whether customer is 65 or older (0 = No, 1 = Yes) |
| `Partner` | `object` | 0 | 2 | Whether the customer has a spouse/partner ('Yes', 'No') |
| `Dependents` | `object` | 0 | 2 | Whether the customer has dependents ('Yes', 'No') |
| `tenure` | `int64` | 0 | 73 | Number of months the customer has stayed with the provider (0 to 72) |
| `PhoneService` | `object` | 0 | 2 | Whether the customer has phone service ('Yes', 'No') |
| `MultipleLines` | `object` | 0 | 3 | Whether the customer has multiple phone lines ('Yes', 'No', 'No phone service') |
| `InternetService` | `object` | 0 | 3 | Customer internet service tier ('DSL', 'Fiber optic', 'No') |
| `OnlineSecurity` | `object` | 0 | 3 | Online security add-on subscription ('Yes', 'No', 'No internet service') |
| `OnlineBackup` | `object` | 0 | 3 | Online backup add-on subscription ('Yes', 'No', 'No internet service') |
| `DeviceProtection` | `object` | 0 | 3 | Device protection add-on subscription ('Yes', 'No', 'No internet service') |
| `TechSupport` | `object` | 0 | 3 | Dedicated technical support add-on ('Yes', 'No', 'No internet service') |
| `StreamingTV` | `object` | 0 | 3 | Streaming TV add-on subscription ('Yes', 'No', 'No internet service') |
| `StreamingMovies` | `object` | 0 | 3 | Streaming movies add-on subscription ('Yes', 'No', 'No internet service') |
| `Contract` | `object` | 0 | 3 | Contract term ('Month-to-month', 'One year', 'Two year') |
| `PaperlessBilling` | `object` | 0 | 2 | Whether paperless billing is active ('Yes', 'No') |
| `PaymentMethod` | `object` | 0 | 4 | Billing payment method ('Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)') |
| `MonthlyCharges` | `float64` | 0 | 1,585 | Current monthly recurring charge in USD |
| `TotalCharges` | `float64` | 0 | 6,531 | Cumulative total charges billed to the customer in USD (imputed 0.0 for tenure=0) |
| `Churn` | `object` | 0 | 2 | Target variable indicating whether customer cancelled service ('Yes', 'No') |
| `TotalCharges_Imputed_Flag` | `int64` | 0 | 2 | Audit flag: 1 if raw TotalCharges was blank (tenure=0), 0 otherwise |
| `Churn_Flag` | `int64` | 0 | 2 | Numeric binary churn indicator (1 = Churned, 0 = Retained) |
| `SeniorCitizen_Label` | `object` | 0 | 2 | Human-readable Senior Citizen status ('Yes', 'No') for Power BI/reporting |
| `tenure_group` | `object` | 0 | 4 | Tenure cohort band ('0-12 Months', '13-24 Months', '25-48 Months', '49-72 Months') |
| `customer_segment` | `object` | 0 | 4 | Lifecycle and contract segment ('New Month-to-Month (<=12m)', 'Established Month-to-Month (>12m)', 'One-Year Contract', 'Two-Year Contract') |
| `addon_service_count` | `int64` | 0 | 7 | Count of active internet add-on services (0 to 6) |
| `is_auto_pay` | `int64` | 0 | 2 | Binary flag: 1 if payment method is automatic bank transfer or credit card, 0 otherwise |
| `has_family` | `int64` | 0 | 2 | Binary flag: 1 if customer has a Partner or Dependents, 0 otherwise |
