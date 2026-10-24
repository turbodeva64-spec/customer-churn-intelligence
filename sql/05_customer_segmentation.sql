-- ============================================================================
-- File: sql/05_customer_segmentation.sql
-- Purpose: Multi-dimensional customer segmentation using CASE expressions,
--          value-risk matrices, and support bundle attachment analysis.
-- ============================================================================

-- Query 8 & 10: Churn and Revenue Exposure by Demographic & Household Segment
SELECT
    SeniorStatus,
    CASE
        WHEN Partner = 'Yes' AND Dependents = 'Yes' THEN 'Family (Partner + Dependents)'
        WHEN Partner = 'Yes' AND Dependents = 'No' THEN 'Couple (Partner Only)'
        WHEN Partner = 'No' AND Dependents = 'Yes' THEN 'Single Parent (Dependents Only)'
        ELSE 'Single Individual'
    END AS household_segment,
    COUNT(*) AS total_customers,
    SUM(Churn_Binary) AS churned_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
FROM vw_telco_cleaned
GROUP BY SeniorStatus, household_segment
ORDER BY churn_rate_pct DESC;

-- Query 11: Customer Behavioral & Value-Risk Segmentation Using CASE
SELECT
    CASE
        WHEN Contract = 'Month-to-month' AND InternetService = 'Fiber optic' AND tenure <= 12
            THEN 'Tier 1: Critical Early Fiber M2M (<=12m)'
        WHEN Contract = 'Month-to-month' AND InternetService = 'Fiber optic' AND tenure > 12
            THEN 'Tier 2: Established Fiber M2M (>12m)'
        WHEN Contract = 'Month-to-month' AND InternetService = 'DSL'
            THEN 'Tier 3: DSL Month-to-Month'
        WHEN Contract = 'Month-to-month' AND InternetService = 'No'
            THEN 'Tier 4: Voice-Only Month-to-Month'
        WHEN Contract IN ('One year', 'Two year') AND InternetService = 'Fiber optic'
            THEN 'Tier 5: Committed Fiber (1-2 Yr)'
        ELSE 'Tier 6: Committed DSL / Voice (1-2 Yr)'
    END AS strategic_segment,
    COUNT(*) AS customer_count,
    SUM(Churn_Binary) AS churned_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(MonthlyCharges), 2) AS total_mrr_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
FROM vw_telco_cleaned
GROUP BY strategic_segment
ORDER BY churn_rate_pct DESC;

-- Security & TechSupport Attachment Impact on Fiber Optic & DSL Customers
SELECT
    InternetService,
    OnlineSecurity,
    TechSupport,
    COUNT(*) AS customer_count,
    SUM(Churn_Binary) AS churned_customers,
    ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
FROM vw_telco_cleaned
WHERE InternetService IN ('Fiber optic', 'DSL')
GROUP BY InternetService, OnlineSecurity, TechSupport
ORDER BY InternetService, churn_rate_pct DESC;
