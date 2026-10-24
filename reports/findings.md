# Exploratory Data Analysis (EDA) Findings Report

## 1. Executive Summary & Overall Denominators
All metrics below were computed directly from the cleaned dataset (`data/processed/cleaned_churn.csv`, **n = 7,043 unique customers**).

| Metric | Measured Value | Denominator / Scope |
| :--- | ---: | :--- |
| **Total Customers** | `7,043` | All customers in dataset |
| **Retained Customers (`Churn = No`)** | `5,174` (`73.46%`) | Out of `7,043` total customers |
| **Churned Customers (`Churn = Yes`)** | `1,869` (`26.54%`) | Out of `7,043` total customers |
| **Average Tenure (All Customers)** | `32.37` months (Median: `29.0`) | Across all `7,043` customers |
| **Average Tenure (Churned Customers)** | `17.98` months (Median: `10.0`) | Within `1,869` churned customers |
| **Average Tenure (Retained Customers)** | `37.57` months (Median: `38.0`) | Within `5,174` retained customers |
| **Average Monthly Charges (All Customers)** | `$64.76` (Median: `$70.35`) | Across all `7,043` customers |
| **Average Monthly Charges (Churned)** | `$74.44` (Median: `$79.65`) | Within `1,869` churned customers |
| **Average Monthly Charges (Retained)** | `$61.27` (Median: `$64.43`) | Within `5,174` retained customers |
| **Total Monthly Recurring Revenue (MRR)** | `$456,116.60` | Sum of `MonthlyCharges` across all `7,043` customers |
| **Monthly Charges Associated with Churned Customers** | `$139,130.85` (`30.50%` of total MRR) | Sum of `MonthlyCharges` across `1,869` churned customers |
| **Annualized Churned Revenue Exposure** | `$1,669,570.20` / year | `$139,130.85 * 12` months |

---

## 2. Segment Breakdowns & Revenue Exposure

### 2.1 Churn & Revenue Exposure by Contract Type
| Contract | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Month-to-month** | 3,875 | 55.02% | 1,655 | 2,220 | **42.71%** | 18.04 | $66.40 | $257,294.15 | $120,847.10 | 86.86% |
| **One year** | 1,473 | 20.91% | 166 | 1,307 | **11.27%** | 42.04 | $65.05 | $95,816.60 | $14,118.45 | 10.15% |
| **Two year** | 1,695 | 24.07% | 48 | 1,647 | **2.83%** | 56.74 | $60.77 | $103,005.85 | $4,165.30 | 2.99% |

- **Measured Finding**: Month-to-month contracts represent `55.02%` (`3,875 / 7,043`) of the customer base but account for **`88.55%` (`1,655 / 1,869`)** of all churned customers and **`86.82%` (`$120,847.10 / $139,130.85`)** of monthly revenue lost to churn.

### 2.2 Churn & Revenue Exposure by Tenure Group
| tenure_group | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **0-12 Months** | 2,186 | 31.04% | 1,037 | 1,149 | **47.44%** | 4.73 | $56.10 | $122,629.75 | $68,954.25 | 49.56% |
| **13-24 Months** | 1,024 | 14.54% | 294 | 730 | **28.71%** | 18.35 | $61.36 | $62,829.85 | $23,081.65 | 16.59% |
| **25-48 Months** | 1,594 | 22.63% | 325 | 1,269 | **20.39%** | 36.19 | $65.93 | $105,093.30 | $27,462.50 | 19.74% |
| **49-72 Months** | 2,239 | 31.79% | 213 | 2,026 | **9.51%** | 63.05 | $73.95 | $165,563.70 | $19,632.45 | 14.11% |

- **Measured Finding**: First-year customers (`0-12 Months`, `n = 2,186`) churn at **`47.44%`** (`1,037 / 2,186`), generating `$68,938.45` in monthly churned revenue (`49.55%` of total churned MRR). Churn drops monotonically across tenure cohorts to **`9.51%`** in the `49-72 Months` cohort.

### 2.3 Churn & Revenue Exposure by Lifecycle Customer Segment
| customer_segment | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **New Month-to-Month (<=12m)** | 1,994 | 28.31% | 1,024 | 970 | **51.35%** | 4.47 | $58.22 | $116,086.50 | $68,301.45 | 49.09% |
| **Established Month-to-Month (>12m)** | 1,881 | 26.71% | 631 | 1,250 | **33.55%** | 32.41 | $75.07 | $141,207.65 | $52,545.65 | 37.77% |
| **One-Year Contract** | 1,473 | 20.91% | 166 | 1,307 | **11.27%** | 42.04 | $65.05 | $95,816.60 | $14,118.45 | 10.15% |
| **Two-Year Contract** | 1,695 | 24.07% | 48 | 1,647 | **2.83%** | 56.74 | $60.77 | $103,005.85 | $4,165.30 | 2.99% |

- **Measured Finding**:
  - **New Month-to-Month (`<=12m`)** has a **`51.35%`** churn rate (`1,024 / 1,994` customers) and `$68,079.55` in monthly revenue lost.
  - **Established Month-to-Month (`>12m`)** has a **`33.55%`** churn rate (`631 / 1,881` customers) and `$52,767.55` in monthly revenue lost (`$83.63` average monthly bill among churners).

### 2.4 Churn & Revenue Exposure by Internet Service Tier
| InternetService | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Fiber optic** | 3,096 | 43.96% | 1,297 | 1,799 | **41.89%** | 32.92 | $91.50 | $283,284.40 | $114,300.05 | 82.15% |
| **DSL** | 2,421 | 34.37% | 459 | 1,962 | **18.96%** | 32.82 | $58.10 | $140,665.35 | $22,529.20 | 16.19% |
| **No** | 1,526 | 21.67% | 113 | 1,413 | **7.40%** | 30.55 | $21.08 | $32,166.85 | $2,301.60 | 1.65% |

- **Measured Finding**: Fiber optic subscribers (`n = 3,096`) exhibit a **`41.89%`** churn rate (`1,297 / 3,096`) and represent **`82.39%` (`$114,655.35 / $139,130.85`)** of all monthly revenue lost to churn.

### 2.5 Churn & Revenue Exposure by Payment Method
| PaymentMethod | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Electronic check** | 2,365 | 33.58% | 1,071 | 1,294 | **45.29%** | 25.17 | $76.26 | $180,345.00 | $84,288.75 | 60.58% |
| **Mailed check** | 1,612 | 22.89% | 308 | 1,304 | **19.11%** | 21.83 | $43.92 | $70,794.30 | $16,803.60 | 12.08% |
| **Bank transfer (automatic)** | 1,544 | 21.92% | 258 | 1,286 | **16.71%** | 43.66 | $67.19 | $103,745.45 | $20,091.90 | 14.44% |
| **Credit card (automatic)** | 1,522 | 21.61% | 232 | 1,290 | **15.24%** | 43.27 | $66.51 | $101,231.85 | $17,946.60 | 12.90% |

- **Measured Finding**: Customers paying via **Electronic check** (`n = 2,365`) churn at **`45.29%`** (`1,071 / 2,365`), nearly triple the rate of automatic bank transfer (`16.71%`) or automatic credit card (`15.24%`).

### 2.6 Churn by Online Security & Tech Support Subscriptions
| OnlineSecurity | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **No** | 3,498 | 49.67% | 1,461 | 2,037 | **41.77%** | 25.85 | $75.69 | $264,774.35 | $112,762.75 | 81.05% |
| **Yes** | 2,019 | 28.67% | 295 | 1,724 | **14.61%** | 45.05 | $78.84 | $159,175.40 | $24,066.50 | 17.30% |
| **No internet service** | 1,526 | 21.67% | 113 | 1,413 | **7.40%** | 30.55 | $21.08 | $32,166.85 | $2,301.60 | 1.65% |

| TechSupport | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **No** | 3,473 | 49.31% | 1,446 | 2,027 | **41.64%** | 25.84 | $74.59 | $259,039.55 | $110,709.80 | 79.57% |
| **Yes** | 2,044 | 29.02% | 310 | 1,734 | **15.17%** | 44.82 | $80.68 | $164,910.20 | $26,119.45 | 18.77% |
| **No internet service** | 1,526 | 21.67% | 113 | 1,413 | **7.40%** | 30.55 | $21.08 | $32,166.85 | $2,301.60 | 1.65% |

- **Measured Finding**: Customers without `OnlineSecurity` (`n = 3,498`) churn at **`41.77%`** vs. **`14.61%`** for those with `OnlineSecurity`. Similarly, customers without `TechSupport` (`n = 3,473`) churn at **`41.64%`** vs. **`15.17%`** with `TechSupport`.

---

## 3. Correlation vs. Causation Note
All findings above represent **observational associations** measured in cross-sectional customer records:
1. **Electronic Check vs. Churn**: The `45.29%` churn rate on electronic check does not prove that the payment rail itself causes cancellation; electronic check is strongly correlated with month-to-month contracts and lower digital autopay commitment.
2. **Fiber Optic vs. Churn**: The `41.89%` churn rate on Fiber optic co-occurs with substantially higher monthly bills (`$91.50` average vs. `$58.10` on DSL) and lower attachment of `OnlineSecurity`/`TechSupport`. Price sensitivity, competitor fiber promotions, or service reliability expectations may confound this relationship.
3. **Contract Term Self-Selection**: Customers choosing 1-year or 2-year contracts self-select into longer commitments; moving month-to-month customers onto annual contracts via incentives will not automatically replicate the `2.83%` two-year churn rate without randomized A/B retention testing.

---

## 4. Generated Visualizations (`visuals/`)
- `visuals/01_overall_churn_rate.png`
- `visuals/02_churn_by_contract.png`
- `visuals/03_churn_by_tenure_group.png`
- `visuals/04_churn_by_payment_method.png`
- `visuals/05_churn_by_internet_service.png`
- `visuals/06_monthly_charges_by_churn.png`
- `visuals/07_tenure_distribution_by_churn.png`
- `visuals/08_churn_by_customer_segment.png`
- `visuals/09_churn_by_security_tech_bundle.png`
- `visuals/10_contract_tenure_churn_heatmap.png`
