-- ============================================================================
-- File: sql/04_churn_analysis.sql
-- Purpose: Dimensional churn and revenue exposure analysis across Contract,
--          Tenure Group, Payment Method, and Internet/Service Type.
-- ============================================================================

-- Query 4: Churn and Revenue Exposure by Contract Type
SELECT
    Contract,
    COUNT(*) AS total_customers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM vw_telco_cleaned), 2) AS customer_share_pct,
    SUM(Churn_Binary) AS churned_customers,
    COUNT(*) - SUM(Churn_Binary) AS retained_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END) /
          (SELECT SUM(MonthlyCharges) FROM vw_telco_cleaned WHERE Churn = 'Yes'), 2) AS share_of_total_churned_mrr_pct
FROM vw_telco_cleaned
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- Query 5: Churn and Revenue Exposure by Tenure Group
SELECT
    Tenure_Group,
    COUNT(*) AS total_customers,
    SUM(Churn_Binary) AS churned_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
FROM vw_telco_cleaned
GROUP BY Tenure_Group
ORDER BY MIN(tenure) ASC;

-- Query 6: Churn and Revenue Exposure by Payment Method
SELECT
    PaymentMethod,
    CASE WHEN Is_AutoPay = 1 THEN 'Auto-Pay' ELSE 'Manual Billing' END AS billing_automation,
    COUNT(*) AS total_customers,
    SUM(Churn_Binary) AS churned_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
FROM vw_telco_cleaned
GROUP BY PaymentMethod, billing_automation
ORDER BY churn_rate_pct DESC;

-- Query 7: Churn and Revenue Exposure by Internet Service Tier
SELECT
    InternetService,
    COUNT(*) AS total_customers,
    SUM(Churn_Binary) AS churned_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
FROM vw_telco_cleaned
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;
