-- ============================================================================
-- File: sql/02_data_quality.sql
-- Purpose: Data-quality audit queries (duplicates, missing/blank values,
--          domain range checks, and zero-tenure TotalCharges reconciliation).
-- ============================================================================

-- Query 14a: Primary Key Uniqueness & Null Audit
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT customerID) AS unique_customers,
    COUNT(*) - COUNT(DISTINCT customerID) AS duplicate_customer_ids,
    SUM(CASE WHEN customerID IS NULL OR TRIM(customerID) = '' THEN 1 ELSE 0 END) AS null_or_blank_ids,
    SUM(CASE WHEN TotalCharges IS NULL OR TRIM(TotalCharges) = '' THEN 1 ELSE 0 END) AS blank_total_charges,
    SUM(CASE WHEN tenure = 0 THEN 1 ELSE 0 END) AS zero_tenure_rows,
    SUM(CASE WHEN (TotalCharges IS NULL OR TRIM(TotalCharges) = '') AND tenure = 0 THEN 1 ELSE 0 END) AS blank_charges_with_zero_tenure
FROM customer_churn_raw;

-- Query 14b: Inspect All 11 Records with Blank TotalCharges
SELECT
    customerID,
    gender,
    SeniorCitizen,
    Partner,
    Dependents,
    tenure,
    Contract,
    InternetService,
    PaymentMethod,
    MonthlyCharges,
    TotalCharges,
    Churn
FROM customer_churn_raw
WHERE TotalCharges IS NULL OR TRIM(TotalCharges) = ''
ORDER BY MonthlyCharges DESC;

-- Query 14c: Logical Service Consistency Check (No Internet vs Add-on Services)
SELECT
    InternetService,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN OnlineSecurity = 'Yes' OR OnlineBackup = 'Yes' OR DeviceProtection = 'Yes'
              OR TechSupport = 'Yes' OR StreamingTV = 'Yes' OR StreamingMovies = 'Yes'
        THEN 1 ELSE 0 END) AS invalid_addon_flags
FROM customer_churn_raw
GROUP BY InternetService;
