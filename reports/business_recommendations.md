# Executive Business Recommendations & Retention Strategy

> **Methodological Note**: All metrics in Section 1 are **measured facts** from `data/raw/telco_churn.db` (`7,043` customers) and `models/training_metrics.json`. All campaign projections in Section 2 are explicitly labeled as **hypothetical scenario simulations** based on our holdout test set (`N = 1,409`).

## 1. Prioritized Retention Interventions (Grounded in Measured Findings)

### Priority 1: Month-to-Month to 1-Year Contract Migration Campaign
- **Target Segment**: Month-to-month subscribers (`3,875` customers, `55.02%` of base), specifically focusing on those in months `3–12` of tenure with Fiber Optic service.
- **Measured Evidence**: Month-to-month customers churn at **42.71%** (`1,655 / 3,875`) and account for **$120,847.10/month** (`86.86%`) of all churned MRR, compared to **11.27%** for One-year contracts and **2.83%** for Two-year contracts.
- **Recommended Action**: Offer a **1-month bill credit or $10/month loyalty discount** upon upgrading from a Month-to-month plan to a 12-month contract at the 90-day onboarding milestone.

### Priority 2: Fiber Optic "Tech Support & Online Security" Value Bundle
- **Target Segment**: Fiber Optic subscribers lacking both `OnlineSecurity` and `TechSupport` (`1,859` customers).
- **Measured Evidence**: Fiber Optic subscribers overall churn at **41.89%** (`$114,300.05` MRR lost). Within Fiber Optic, customers without `OnlineSecurity` (`No`) churn at **49.36%** vs. **21.81%** with `OnlineSecurity`, and those without `TechSupport` (`No`) churn at **49.37%** vs. **22.63%** with `TechSupport`.
- **Recommended Action**: Bundle complimentary 6-month **Online Security + Tech Support** into Fiber Optic onboarding packages to increase service stickiness (`Total_Services_Count`) and resolve early connectivity friction.

### Priority 3: Electronic Check to Auto-Pay Conversion Incentive
- **Target Segment**: Customers paying via `Electronic check` (`2,365` customers, `33.58%` of base).
- **Measured Evidence**: Electronic check users exhibit a **45.29% churn rate** (`1,071` churned customers; **$84,288.75** MRR lost—`60.58%` of all churned MRR), whereas automatic payment methods (`Bank transfer` and `Credit card`) churn at **16.71%** and **15.24%**, respectively.
- **Recommended Action**: Trigger an automated in-app/email prompt offering a **$5/month Auto-Pay discount** (or one-time $15 credit) when customers switch from Electronic Check to automatic bank transfer or credit card billing.

### Priority 4: First-Year ("0–12 Month") Proactive Onboarding Cadence
- **Target Segment**: New subscribers in their first 12 months (`2,186` customers).
- **Measured Evidence**: Churn peaks sharply in the `0-12m` cohort at **47.44%** (`1,037 / 2,186`, representing `55.48%` of all churned customers), with median churned tenure at **10.0 months** (mean `17.98` months vs. `37.57` months for retained customers).
- **Recommended Action**: Deploy automated health checks at Day 15, Day 45, and Day 90 for customers with `Churn_Probability >= 0.45` (`data/predictions/customer_risk_predictions.csv`).

---

## 2. Hypothetical Campaign ROI Simulation (Holdout Test Set, N = 1,409)
- **Explicit Assumptions (Hypothetical)**:
  - Intervention cost per contacted customer (outreach + incentive): **$25.00**
  - Retained value per saved churner (6 months of average churned MRR `$74.44` x `25%` conversion rate): **$150.00 expected value per true positive** (`TP * $150 - (TP + FP) * $25`).
- **Measured Threshold Trade-Offs on Test Set**:
  - **Default Threshold (`0.50`)**: Flags `291` customers (Logistic Regression: `TP = 201`, `FP = 90`, Precision = `69.07%`, Recall = `53.74%`) -> Simulated Net Benefit = **$22,875**.
  - **Profit-Optimal Campaign Threshold (`0.25`)**: Flags `569` customers (Logistic Regression: `TP = 319`, `FP = 250`, Precision = `56.06%`, Recall = `85.29%`) -> Simulated Net Benefit = **$33,625** (`+47.0%` higher net retention value than default `0.50` threshold).
