-- ============================================================================
-- File: sql/01_schema.sql
-- Dialect: SQLite 3.40+ (with PostgreSQL 15+ compatibility notes)
-- Purpose: Production schema DDL and analytical view definitions for
--          Telco Customer Churn Intelligence.
-- ============================================================================

CREATE TABLE IF NOT EXISTS customer_churn_raw (
    customerID TEXT PRIMARY KEY,
    gender TEXT NOT NULL,
    SeniorCitizen INTEGER NOT NULL CHECK (SeniorCitizen IN (0, 1)),
    Partner TEXT NOT NULL CHECK (Partner IN ('Yes', 'No')),
    Dependents TEXT NOT NULL CHECK (Dependents IN ('Yes', 'No')),
    tenure INTEGER NOT NULL CHECK (tenure >= 0),
    PhoneService TEXT NOT NULL CHECK (PhoneService IN ('Yes', 'No')),
    MultipleLines TEXT NOT NULL,
    InternetService TEXT NOT NULL CHECK (InternetService IN ('DSL', 'Fiber optic', 'No')),
    OnlineSecurity TEXT NOT NULL,
    OnlineBackup TEXT NOT NULL,
    DeviceProtection TEXT NOT NULL,
    TechSupport TEXT NOT NULL,
    StreamingTV TEXT NOT NULL,
    StreamingMovies TEXT NOT NULL,
    Contract TEXT NOT NULL CHECK (Contract IN ('Month-to-month', 'One year', 'Two year')),
    PaperlessBilling TEXT NOT NULL CHECK (PaperlessBilling IN ('Yes', 'No')),
    PaymentMethod TEXT NOT NULL,
    MonthlyCharges REAL NOT NULL CHECK (MonthlyCharges >= 0),
    TotalCharges TEXT,
    Churn TEXT NOT NULL CHECK (Churn IN ('Yes', 'No'))
);

CREATE INDEX IF NOT EXISTS idx_telco_contract ON customer_churn_raw(Contract);
CREATE INDEX IF NOT EXISTS idx_telco_internet ON customer_churn_raw(InternetService);
CREATE INDEX IF NOT EXISTS idx_telco_payment ON customer_churn_raw(PaymentMethod);
CREATE INDEX IF NOT EXISTS idx_telco_churn ON customer_churn_raw(Churn);
CREATE INDEX IF NOT EXISTS idx_telco_tenure ON customer_churn_raw(tenure);

-- Cleaned Analytical View (handles 11 whitespace TotalCharges rows where tenure = 0)
DROP VIEW IF EXISTS vw_telco_cleaned;
CREATE VIEW vw_telco_cleaned AS
SELECT
    customerID,
    gender,
    SeniorCitizen,
    CASE WHEN SeniorCitizen = 1 THEN 'Senior Citizen' ELSE 'Non-Senior' END AS SeniorStatus,
    Partner,
    Dependents,
    tenure,
    CASE
        WHEN tenure <= 12 THEN '0-12 Months ( Year 1 )'
        WHEN tenure <= 24 THEN '13-24 Months ( Year 2 )'
        WHEN tenure <= 48 THEN '25-48 Months ( Years 3-4 )'
        WHEN tenure <= 60 THEN '49-60 Months ( Year 5 )'
        ELSE '61-72 Months ( Year 6 )'
    END AS Tenure_Group,
    PhoneService,
    MultipleLines,
    InternetService,
    OnlineSecurity,
    OnlineBackup,
    DeviceProtection,
    TechSupport,
    StreamingTV,
    StreamingMovies,
    (CASE WHEN OnlineSecurity = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN OnlineBackup = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN DeviceProtection = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN TechSupport = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN StreamingTV = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN StreamingMovies = 'Yes' THEN 1 ELSE 0 END) AS Addon_Services_Count,
    Contract,
    PaperlessBilling,
    PaymentMethod,
    CASE WHEN PaymentMethod LIKE '%(automatic)%' THEN 1 ELSE 0 END AS Is_AutoPay,
    MonthlyCharges,
    CASE
        WHEN TRIM(COALESCE(TotalCharges, '')) = '' THEN 0.0
        ELSE CAST(TRIM(TotalCharges) AS REAL)
    END AS TotalCharges_Cleaned,
    CASE
        WHEN TRIM(COALESCE(TotalCharges, '')) = '' THEN 1
        ELSE 0
    END AS TotalCharges_Imputed_Flag,
    Churn,
    CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END AS Churn_Binary
FROM customer_churn_raw;
