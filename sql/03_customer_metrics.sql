-- ============================================================================
-- File: sql/03_customer_metrics.sql
-- Purpose: Core executive KPIs (Total customers, Churned/Retained counts,
--          Overall churn rate, Average tenure, Average monthly charges, and
--          Monthly charges associated with churned customers).
-- ============================================================================

-- Query 1, 2, 3, & 9: Executive Customer & Revenue Exposure Summary
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS retained_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS overall_churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_all_customers_months,
    ROUND(AVG(CASE WHEN Churn = 'Yes' THEN tenure END), 2) AS avg_tenure_churned_months,
    ROUND(AVG(CASE WHEN Churn = 'No' THEN tenure END), 2) AS avg_tenure_retained_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_all_usd,
    ROUND(AVG(CASE WHEN Churn = 'Yes' THEN MonthlyCharges END), 2) AS avg_monthly_charges_churned_usd,
    ROUND(AVG(CASE WHEN Churn = 'No' THEN MonthlyCharges END), 2) AS avg_monthly_charges_retained_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_recurring_revenue_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_monthly_revenue_exposure_usd,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END) / SUM(MonthlyCharges), 2) AS mrr_exposure_share_pct
FROM vw_telco_cleaned;

-- Breakdown by Churn Status (Explicit Group Denominators)
SELECT
    Churn AS churn_status,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM vw_telco_cleaned), 2) AS pct_of_total_customers,
    ROUND(AVG(tenure), 2) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges_usd,
    ROUND(AVG(TotalCharges_Cleaned), 2) AS avg_total_charges_usd,
    ROUND(SUM(TotalCharges_Cleaned), 2) AS cumulative_total_charges_usd
FROM vw_telco_cleaned
GROUP BY Churn
ORDER BY Churn DESC;
