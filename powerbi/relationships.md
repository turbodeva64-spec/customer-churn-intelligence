# Power BI Star Schema & Relationship Architecture

## 1. Star-Schema Design Overview
To ensure optimal VertiPaq compression and zero ambiguous filter paths in Power BI, the cleaned dataset and ML risk predictions are exported (`src/export_powerbi.py`) into a normalized Star Schema inside `data/processed/powerbi/`:

| Table Name | Table Role | Row Count | Primary / Foreign Key | Description |
| :--- | :--- | :---: | :--- | :--- |
| `Fact_Customer_Churn.csv` | Fact Table | 7,043 | `customerID` (PK) | Numerical measures (`tenure`, `MonthlyCharges`, `TotalCharges`, `Total_Services_Count`), `Churn_Binary`, and ML predictions (`Churn_Probability`, `Predicted_Risk_Tier`, `Expected_Monthly_Revenue_Loss`) |
| `Dim_Customer_Profile.csv` | Dimension | 7,043 | `customerID` (PK/FK) | Demographic & lifecycle segments (`gender`, `SeniorCitizen`, `Senior_Label`, `Partner`, `Dependents`, `Tenure_Group`) |
| `Dim_Service_Subscription.csv` | Dimension | 7,043 | `customerID` (PK/FK) | Connectivity & add-on flags (`PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Has_Tech_Or_Security`) |
| `Dim_Billing_Contract.csv` | Dimension | 7,043 | `customerID` (PK/FK) | Commercial terms (`Contract`, `PaperlessBilling`, `PaymentMethod`, `Is_AutoPay`) |
| `Summary_Segment_KPIs.csv` | Reference Table | 35 | Composite (`Contract`, `InternetService`, `Tenure_Group`) | Pre-aggregated validation table for QA cross-checking |

## 2. Relationship Configuration Rules
- **Cardinality**: `1-to-1` (or `1-to-Many` from `Dim_*` to `Fact_Customer_Churn` on `customerID`).
- **Cross-Filter Direction**: Set to **Single** (`Dim_*` filters `Fact_Customer_Churn`) to prevent circular dependency traps and maintain deterministic DAX evaluation.
- **Active Status**: All three dimension relationships (`Dim_Customer_Profile[customerID]`, `Dim_Service_Subscription[customerID]`, `Dim_Billing_Contract[customerID]`) are **Active**.
