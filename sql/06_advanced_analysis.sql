-- ============================================================================
-- File: sql/06_advanced_analysis.sql
-- Purpose: Advanced SQL analytics using Common Table Expressions (CTEs),
--          Window Functions (RANK, DENSE_RANK, NTILE, cumulative sums),
--          and Customer-Level Retention Prioritization.
-- ============================================================================

-- Query 12 & 13: CTE + Window Functions for Segment Ranking & Cumulative Revenue Exposure
WITH segment_aggregation AS (
    SELECT
        Contract,
        InternetService,
        PaymentMethod,
        COUNT(*) AS customer_count,
        SUM(Churn_Binary) AS churned_customers,
        ROUND(100.0 * SUM(Churn_Binary) / COUNT(*), 2) AS churn_rate_pct,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_usd,
        ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr_usd,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr_exposure_usd
    FROM vw_telco_cleaned
    GROUP BY Contract, InternetService, PaymentMethod
    HAVING COUNT(*) >= 30
),
ranked_segments AS (
    SELECT
        Contract,
        InternetService,
        PaymentMethod,
        customer_count,
        churned_customers,
        churn_rate_pct,
        avg_monthly_charges_usd,
        total_segment_mrr_usd,
        churned_mrr_exposure_usd,
        DENSE_RANK() OVER (ORDER BY churn_rate_pct DESC) AS churn_rate_rank,
        DENSE_RANK() OVER (ORDER BY churned_mrr_exposure_usd DESC) AS mrr_risk_rank,
        ROUND(100.0 * churned_mrr_exposure_usd / SUM(churned_mrr_exposure_usd) OVER (), 2) AS pct_of_total_churned_mrr,
        ROUND(100.0 * SUM(churned_mrr_exposure_usd) OVER (
            ORDER BY churned_mrr_exposure_usd DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / SUM(churned_mrr_exposure_usd) OVER (), 2) AS cumulative_churned_mrr_pct
    FROM segment_aggregation
)
SELECT *
FROM ranked_segments
ORDER BY mrr_risk_rank ASC
LIMIT 15;

-- Query 15: Customer-Level Retention Prioritization & Risk Scoring (Active Customers)
WITH active_customer_risk AS (
    SELECT
        customerID,
        Contract,
        InternetService,
        PaymentMethod,
        tenure,
        MonthlyCharges,
        TotalCharges_Cleaned,
        Addon_Services_Count,
        -- Heuristic SQL Risk Score (0-100 scale) based on empirical risk factors
        (CASE WHEN Contract = 'Month-to-month' THEN 40
              WHEN Contract = 'One year' THEN 10
              ELSE 0 END +
         CASE WHEN InternetService = 'Fiber optic' THEN 25
              WHEN InternetService = 'DSL' THEN 10
              ELSE 0 END +
         CASE WHEN PaymentMethod = 'Electronic check' THEN 15
              WHEN Is_AutoPay = 0 THEN 5
              ELSE 0 END +
         CASE WHEN tenure <= 12 THEN 15
              WHEN tenure <= 24 THEN 8
              ELSE 0 END +
         CASE WHEN OnlineSecurity = 'No' AND TechSupport = 'No' AND InternetService != 'No' THEN 5
              ELSE 0 END) AS sql_risk_score,
        NTILE(4) OVER (ORDER BY MonthlyCharges DESC) AS mrr_value_quartile
    FROM vw_telco_cleaned
    WHERE Churn = 'No'
)
SELECT
    customerID,
    Contract,
    InternetService,
    PaymentMethod,
    tenure,
    MonthlyCharges,
    Addon_Services_Count,
    sql_risk_score,
    mrr_value_quartile,
    ROUND(MonthlyCharges * 12.0, 2) AS annualized_revenue_at_risk_usd,
    CASE
        WHEN sql_risk_score >= 80 AND mrr_value_quartile = 1 THEN 'P1: Immediate High-Value Save Call + 12m Contract Incentive'
        WHEN sql_risk_score >= 70 THEN 'P2: Proactive Auto-Pay & TechSupport Bundle Offer'
        WHEN sql_risk_score >= 50 THEN 'P3: Automated Onboarding & Digital Engagement'
        ELSE 'P4: Standard Loyalty Monitoring'
    END AS recommended_retention_action
FROM active_customer_risk
ORDER BY sql_risk_score DESC, MonthlyCharges DESC
LIMIT 25;
