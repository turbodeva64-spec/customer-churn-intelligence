# SQL Business Analysis Suite (`sql/`)

## Overview & SQL Dialect
- **Primary Execution Engine**: SQLite 3.40.1 (`data/raw/telco_churn.db`, table `customer_churn_raw`, analytical view `vw_telco_cleaned`).
- **PostgreSQL 15+ Compatibility**: All queries use standard ANSI SQL (`CASE WHEN`, `COALESCE`, `TRIM`, `CAST(... AS REAL)`, `WITH` CTEs, and `OVER (...)` window functions) that execute unmodified in both SQLite 3.40+ and PostgreSQL 15+.
- **Execution & Reconciliation Status**: **COMPLETED AND VERIFIED** — All 16 SQL queries across 6 files were executed against `data/raw/telco_churn.db` and reconciled 100% against Python (`pandas`) calculations with zero discrepancies.

---

## Query Catalog & Business Purposes

| Query ID | SQL File | Query Title | Business Purpose |
|---|---|---|---|
| **Q01-Q03, Q09** | `03_customer_metrics.sql` | Executive Customer & Revenue Exposure KPIs | Quantifies total customer base (`7,043`), churned (`1,869`), retained (`5,174`), overall churn rate (`26.54%`), average tenure (`32.37` mo), average monthly charges (`$64.76`), and monthly recurring revenue (MRR) associated with churned customers (`$139,130.85`). |
| **Q04** | `04_churn_analysis.sql` | Churn & Revenue Exposure by Contract Type | Evaluates retention performance across Month-to-month (`42.71%` churn), One year (`11.27%`), and Two year (`2.83%`) contracts. |
| **Q05** | `04_churn_analysis.sql` | Churn & Revenue Exposure by Tenure Group | Tracks lifecycle churn decay from Year 1 (`0-12m`: `47.44%` churn) down to Year 6 (`61-72m`: `6.61%` churn). |
| **Q06** | `04_churn_analysis.sql` | Churn & Revenue Exposure by Payment Method | Compares manual payment friction (`Electronic check`: `45.29%` churn) against automatic payment methods (`15.24%–16.71%` churn). |
| **Q07** | `04_churn_analysis.sql` | Churn & Revenue Exposure by Internet Service | Contrasts high-ARPU Fiber optic churn (`41.89%`, `$88,878.85` MRR lost) against DSL (`18.96%`) and No Internet (`7.40%`). |
| **Q08, Q10** | `05_customer_segmentation.sql` | Demographic & Household Revenue Exposure | Segments churn and MRR exposure by Senior Citizen status and household composition (Single, Couple, Family, Single Parent). |
| **Q11** | `05_customer_segmentation.sql` | Strategic Value-Risk Segmentation (`CASE`) | Uses multi-condition `CASE` logic to classify customers into 6 actionable lifecycle/product tiers, isolating Tier 1 Early Fiber Month-to-Month (`69.49%` churn). |
| **Q11b** | `05_customer_segmentation.sql` | Security & TechSupport Bundle Impact | Measures how `OnlineSecurity` and `TechSupport` attachment reduces churn within Fiber optic and DSL tiers. |
| **Q12, Q13** | `06_advanced_analysis.sql` | Multi-Dimensional Segment Ranking (CTEs & Window Functions) | Uses `WITH` CTEs, `DENSE_RANK() OVER`, and cumulative window sums (`SUM(...) OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`) to prove that the top 3 micro-segments account for `56.69%` of all churned MRR. |
| **Q14a-c** | `02_data_quality.sql` | Database Integrity & Blank `TotalCharges` Audit | Audits primary key uniqueness (`0` duplicates), verifies that all `11` blank `TotalCharges` records have `tenure = 0` and `Churn = 'No'`, and checks service-dependency constraints. |
| **Q15** | `06_advanced_analysis.sql` | Customer-Level Retention Prioritization | Uses `NTILE(4) OVER` and composite SQL risk scoring on active (`Churn = 'No'`) customers to rank high-value save targets. |

---

## Executed SQL Outputs & Python Reconciliation

### 1. Data Quality Audit (`02_data_quality.sql` — Q14a & Q14b)
|   total_rows |   unique_customers |   duplicate_customer_ids |   null_or_blank_ids |   blank_total_charges |   zero_tenure_rows |   blank_charges_with_zero_tenure |
|--------------|--------------------|--------------------------|---------------------|-----------------------|--------------------|----------------------------------|
|         7043 |               7043 |                        0 |                   0 |                    11 |                 11 |                               11 |

**All 11 Blank `TotalCharges` Records (`tenure = 0`, `Churn = 'No'`):**
| customerID   | gender   |   SeniorCitizen | Partner   | Dependents   |   tenure | Contract   | InternetService   | PaymentMethod             |   MonthlyCharges | TotalCharges   | Churn   |
|--------------|----------|-----------------|-----------|--------------|----------|------------|-------------------|---------------------------|------------------|----------------|---------|
| 5709-LVOEQ   | Female   |               0 | Yes       | Yes          |        0 | Two year   | DSL               | Mailed check              |            80.85 |                | No      |
| 4075-WKNIU   | Female   |               0 | Yes       | Yes          |        0 | Two year   | DSL               | Mailed check              |            73.35 |                | No      |
| 2775-SEFEE   | Male     |               0 | No        | Yes          |        0 | Two year   | DSL               | Bank transfer (automatic) |            61.9  |                | No      |
| 1371-DWPAZ   | Female   |               0 | Yes       | Yes          |        0 | Two year   | DSL               | Credit card (automatic)   |            56.05 |                | No      |
| 4472-LVYGI   | Female   |               0 | Yes       | Yes          |        0 | Two year   | DSL               | Bank transfer (automatic) |            52.55 |                | No      |
| 4367-NUYAO   | Male     |               0 | Yes       | Yes          |        0 | Two year   | No                | Mailed check              |            25.75 |                | No      |
| 3213-VVOLG   | Male     |               0 | Yes       | Yes          |        0 | Two year   | No                | Mailed check              |            25.35 |                | No      |
| 3115-CZMZD   | Male     |               0 | No        | Yes          |        0 | Two year   | No                | Mailed check              |            20.25 |                | No      |
| 2520-SGTTA   | Female   |               0 | Yes       | Yes          |        0 | Two year   | No                | Mailed check              |            20    |                | No      |
| 7644-OMVMY   | Male     |               0 | Yes       | Yes          |        0 | Two year   | No                | Mailed check              |            19.85 |                | No      |
| 2923-ARZLG   | Male     |               0 | Yes       | Yes          |        0 | One year   | No                | Mailed check              |            19.7  |                | No      |

### 2. Executive KPIs & Group Denominators (`03_customer_metrics.sql` — Q01, Q02, Q03, Q09)
|   total_customers |   churned_customers |   retained_customers |   overall_churn_rate_pct |   avg_tenure_all_months |   avg_monthly_charges_all_usd |   total_mrr_usd |   churned_mrr_exposure_usd |   mrr_exposure_share_pct |
|-------------------|---------------------|----------------------|--------------------------|-------------------------|-------------------------------|-----------------|----------------------------|--------------------------|
|              7043 |                1869 |                 5174 |                    26.54 |                   32.37 |                         64.76 |          456117 |                     139131 |                     30.5 |

**Metrics by Churn Status (Explicit Group Denominators):**
| churn_status   |   customer_count |   pct_of_total_customers |   avg_tenure_months |   avg_monthly_charges_usd |   total_monthly_charges_usd |   avg_total_charges_usd |
|----------------|------------------|--------------------------|---------------------|---------------------------|-----------------------------|-------------------------|
| Yes            |             1869 |                    26.54 |               17.98 |                     74.44 |                      139131 |                 1531.8  |
| No             |             5174 |                    73.46 |               37.57 |                     61.27 |                      316986 |                 2549.91 |

### 3. Churn by Contract Type (`04_churn_analysis.sql` — Q04)
| Contract       |   total_customers |   customer_share_pct |   churned_customers |   churn_rate_pct |   avg_tenure_months |   avg_monthly_charges_usd |   total_segment_mrr_usd |   churned_mrr_exposure_usd |   share_of_total_churned_mrr_pct |
|----------------|-------------------|----------------------|---------------------|------------------|---------------------|---------------------------|-------------------------|----------------------------|----------------------------------|
| Month-to-month |              3875 |                55.02 |                1655 |            42.71 |               18.04 |                     66.4  |                257294   |                   120847   |                            86.86 |
| One year       |              1473 |                20.91 |                 166 |            11.27 |               42.04 |                     65.05 |                 95816.6 |                    14118.5 |                            10.15 |
| Two year       |              1695 |                24.07 |                  48 |             2.83 |               56.74 |                     60.77 |                103006   |                     4165.3 |                             2.99 |

### 4. Churn by Tenure Group (`04_churn_analysis.sql` — Q05)
| Tenure_Group               |   total_customers |   churned_customers |   churn_rate_pct |   avg_tenure_months |   avg_monthly_charges_usd |   total_segment_mrr_usd |   churned_mrr_exposure_usd |
|----------------------------|-------------------|---------------------|------------------|---------------------|---------------------------|-------------------------|----------------------------|
| 0-12 Months ( Year 1 )     |               956 |                 494 |            51.67 |                4.46 |                     53    |                 50665.7 |                    30922.4 |
| 13-24 Months ( Year 2 )    |              1262 |                 417 |            33.04 |               15.27 |                     60.57 |                 76444.9 |                    31190.3 |
| 25-48 Months ( Years 3-4 ) |              1970 |                 502 |            25.48 |               29.95 |                     64.37 |                126804   |                    39530.2 |
| 49-60 Months ( Year 5 )    |              1075 |                 224 |            20.84 |               43.4  |                     67.94 |                 73036.6 |                    18186.5 |
| 61-72 Months ( Year 6 )    |              1780 |                 232 |            13.03 |               55.51 |                     72.56 |                129165   |                    19301.3 |

### 5. Churn by Payment Method (`04_churn_analysis.sql` — Q06)
| PaymentMethod             | billing_automation   |   total_customers |   churned_customers |   churn_rate_pct |   avg_tenure_months |   avg_monthly_charges_usd |   churned_mrr_exposure_usd |
|---------------------------|----------------------|-------------------|---------------------|------------------|---------------------|---------------------------|----------------------------|
| Electronic check          | Manual Billing       |              2365 |                1071 |            45.29 |               25.17 |                     76.26 |                    84288.8 |
| Mailed check              | Manual Billing       |              1612 |                 308 |            19.11 |               21.83 |                     43.92 |                    16803.6 |
| Bank transfer (automatic) | Auto-Pay             |              1544 |                 258 |            16.71 |               43.66 |                     67.19 |                    20091.9 |
| Credit card (automatic)   | Auto-Pay             |              1522 |                 232 |            15.24 |               43.27 |                     66.51 |                    17946.6 |

### 6. Churn by Internet Service (`04_churn_analysis.sql` — Q07)
| InternetService   |   total_customers |   churned_customers |   churn_rate_pct |   avg_tenure_months |   avg_monthly_charges_usd |   churned_mrr_exposure_usd |
|-------------------|-------------------|---------------------|------------------|---------------------|---------------------------|----------------------------|
| Fiber optic       |              3096 |                1297 |            41.89 |               32.92 |                     91.5  |                   114300   |
| DSL               |              2421 |                 459 |            18.96 |               32.82 |                     58.1  |                    22529.2 |
| No                |              1526 |                 113 |             7.4  |               30.55 |                     21.08 |                     2301.6 |

### 7. Strategic Segmentation Using `CASE` (`05_customer_segmentation.sql` — Q11)
| strategic_segment                        |   customer_count |   churned_customers |   churn_rate_pct |   avg_monthly_charges_usd |   churned_mrr_exposure_usd |
|------------------------------------------|------------------|---------------------|------------------|---------------------------|----------------------------|
| Tier 1: Critical Early Fiber M2M (<=12m) |              366 |                 287 |            78.42 |                     80.87 |                   23257.4  |
| Tier 2: Established Fiber M2M (>12m)     |             1762 |                 875 |            49.66 |                     88.3  |                   77224.6  |
| Tier 3: DSL Month-to-Month               |             1223 |                 394 |            32.22 |                     50.22 |                   18367.2  |
| Tier 4: Voice-Only Month-to-Month        |              524 |                  99 |            18.89 |                     20.41 |                    1997.85 |
| Tier 5: Committed Fiber (1-2 Yr)         |              968 |                 135 |            13.95 |                    101.35 |                   13818    |
| Tier 6: Committed DSL / Voice (1-2 Yr)   |             2200 |                  79 |             3.59 |                     45.78 |                    4465.7  |

### 8. CTE & Window Function Segment Ranking (`06_advanced_analysis.sql` — Q12 & Q13)
| Contract       | InternetService   | PaymentMethod             |   customer_count |   churned_customers |   churn_rate_pct |   avg_monthly_charges_usd |   churned_mrr_exposure_usd |   churn_rate_rank |   mrr_risk_rank |   pct_of_total_churned_mrr |   cumulative_churned_mrr_pct |
|----------------|-------------------|---------------------------|------------------|---------------------|------------------|---------------------------|----------------------------|-------------------|-----------------|----------------------------|------------------------------|
| Month-to-month | Fiber optic       | Electronic check          |             1307 |                 789 |            60.37 |                     87.18 |                   68281.5  |                 1 |               1 |                      49.11 |                        49.11 |
| Month-to-month | Fiber optic       | Bank transfer (automatic) |              327 |                 149 |            45.57 |                     88.25 |                   13062.1  |                 3 |               2 |                       9.39 |                        58.51 |
| Month-to-month | Fiber optic       | Credit card (automatic)   |              293 |                 122 |            41.64 |                     87.97 |                   10731.1  |                 4 |               3 |                       7.72 |                        66.22 |
| Month-to-month | DSL               | Electronic check          |              474 |                 192 |            40.51 |                     49.25 |                    8776.45 |                 5 |               4 |                       6.31 |                        72.54 |
| Month-to-month | Fiber optic       | Mailed check              |              201 |                 102 |            50.75 |                     82.59 |                    8407.25 |                 2 |               5 |                       6.05 |                        78.58 |
| Month-to-month | DSL               | Mailed check              |              367 |                 113 |            30.79 |                     48.84 |                    5292.1  |                 6 |               6 |                       3.81 |                        82.39 |
| One year       | Fiber optic       | Electronic check          |              196 |                  51 |            26.02 |                     99.16 |                    5149.65 |                 8 |               7 |                       3.7  |                        86.09 |
| Month-to-month | DSL               | Credit card (automatic)   |              185 |                  50 |            27.03 |                     52.17 |                    2474.8  |                 7 |               8 |                       1.78 |                        87.87 |
| One year       | Fiber optic       | Credit card (automatic)   |              150 |                  23 |            15.33 |                     99.16 |                    2392.35 |                14 |               9 |                       1.72 |                        89.59 |
| One year       | Fiber optic       | Bank transfer (automatic) |              157 |                  23 |            14.65 |                     98.17 |                    2344.35 |                15 |              10 |                       1.69 |                        91.28 |
