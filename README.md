# Customer Churn Intelligence & Risk Prediction Platform

An end-to-end, enterprise-grade data science, machine learning risk scoring, SQL analytics, and executive Power BI reporting platform built on the **IBM Telco Customer Churn** dataset (**7,043 customers**, **$456,116.60 Monthly Recurring Revenue**).

* **Repository:** [turbodeva64-spec/customer-churn-intelligence](https://github.com/turbodeva64-spec/customer-churn-intelligence)
* **Interactive Dashboard File:** `customer_churn_dashboard.html` (4-View Interactive WebApp with Chart.js, Threshold ROI Simulator & Power BI Segment Workbench)
* **Executive Static Dashboard:** `customer_churn_executive_dashboard.png` (9-Panel High-Resolution Executive Summary consolidating all 13 visuals)

## 1. Unified Executive Dashboard Overview

Every core metric, segment breakdown, distribution curve, heatmap cohort, and machine learning evaluation from the repository's 13 visualizations has been consolidated into a single **Executive Dashboard** (`customer_churn_executive_dashboard.png`) and an interactive **WebApp Dashboard** (`customer_churn_dashboard.html`).



### Executive KPI Scorecard ($N = 7,043$)

| Metric Category | Benchmark Metric | Value | Business & Analytical Context |
| :--- | :--- | :---: | :--- |
| **Customer Volume** | Total Customers ($N$) | **7,043** | Validated primary key (`customerID`) across raw SQLite & Star Schema tables |
| **Customer Retention** | Retained Customers ($Churn = \text{No}$) | **5,174 (73.46%)** | Mean tenure: **37.57 months** (Median: **38.0m**); Avg monthly charge: **$61.27** |
| **Customer Attrition** | Churned Customers ($Churn = \text{Yes}$) | **1,869 (26.54%)** | Mean tenure: **17.98 months** (Median: **10.0m**); Avg monthly charge: **$74.44** |
| **Revenue Baseline** | Total Monthly Recurring Revenue (MRR) | **$456,116.60** | Mean monthly charge across all customers: **$64.76** (Median: **$70.35**) |
| **Revenue at Risk** | Churned Monthly Revenue Exposure | **$139,130.85 (30.50%)** | Annualized churn revenue loss equals **$1,669,570.20 / year** |
| **High-Risk Cohort** | Predicted High-Risk Customers ($P \ge 0.60$) | **785 (11.15%)** | Generates **$44,421.32** in Expected Monthly Revenue Loss ($\sum \text{MRR}_i \times P_i$) |
| **Champion ML Performance** | Held-Out Test ROC-AUC / PR-AUC ($N=1,409$) | **0.8575 / 0.6843** | Logistic Regression test set (Random Forest Test ROC-AUC: **0.8651**, PR-AUC: **0.6869**) |
| **Threshold Optimization** | Profit- & Recall-Optimal Threshold Window | **0.25 – 0.32** | Lifts recall from **53.74%** (@0.50) to **75.40%–83.42%** and net ROI by **+47.0% (+$33,625)** |

### Text-Based Architecture & Revenue Risk Summary Diagram

```text
+---------------------------------------------------------------------------------------------------+
|                        CUSTOMER CHURN INTELLIGENCE PIPELINE (N = 7,043)                           |
+---------------------------------------------------------------------------------------------------+
|  [Raw Data: Telco CSV / SQLite] ---> [Phase 1-2: Clean & Engineer] ---> [Phase 3: 10 EDA Charts]  |
|   * 7,043 rows, 21 columns            * 11 blank TotalCharges -> 0.0     * Contract, Tenure,      |
|   * Total MRR: $456,116.60            * tenure_group, customer_segment     Payment, Fiber, Addons |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  [Phase 4-5: ML Training & Eval] --> [Phase 6: Batch Risk Scoring] --> [Phase 7: Star Schema BI]  |
|   * 80/20 Stratified Split            * High Risk (>=0.60): 785 cust    * Fact_Customer_Churn     |
|   * 47 Encoded Features (No Leakage)  * Med Risk (0.35-0.59): 1,490     * Dim_Customer_Profile    |
|   * LogReg AUC: 0.8575 | RF: 0.8651   * Low Risk (<0.35): 4,768 cust    * Dim_Service_Subscription|
|   * Optimal Threshold: 0.25 - 0.32    * E[Loss] = MRR * P(Churn)        * Dim_Billing_Contract    |
+---------------------------------------------------------------------------------------------------+
```

## 2. Repository Directory Structure

```text
customer-churn-intelligence/
├── .github/
│   └── workflows/
│       └── tests.yml                         # GitHub Actions CI pipeline running pytest on Python 3.10
├── data/
│   ├── predictions/
│   │   └── customer_risk_predictions.csv     # All 7,043 scored customers with probabilities & risk tiers
│   ├── processed/
│   │   ├── powerbi/                          # Normalized Star-Schema tables for Power BI
│   │   │   ├── Dim_Billing_Contract.csv      # Contract, PaperlessBilling, PaymentMethod (7,043 rows)
│   │   │   ├── Dim_Customer_Profile.csv      # Demographics & Tenure_Group (7,043 rows)
│   │   │   ├── Dim_Service_Subscription.csv  # Connectivity & 6 Add-on flags (7,043 rows)
│   │   │   ├── Fact_Customer_Churn.csv       # Measures, Churn_Binary, Probabilities, E[Loss] (7,043 rows)
│   │   │   └── Summary_Segment_KPIs.csv      # Pre-aggregated cohort reference table (20 cohorts)
│   │   ├── cleaned_churn.csv                 # Cleaned dataset with engineered features (7,043 rows)
│   │   └── data_dictionary.csv               # Schema metadata and column definitions
│   └── README.md
├── models/
│   ├── churn_model_pipeline.pkl              # Serialized scikit-learn ColumnTransformer + Classifier pipeline
│   └── training_metrics.json                 # 5-fold CV and train/test metadata
├── notebooks/
│   ├── 01_database_inspection.ipynb          # Interactive schema & anomaly exploration
│   ├── 02_data_cleaning.ipynb                # Imputation and feature engineering walkthrough
│   ├── 03_exploratory_analysis.ipynb         # Segment KPI tables and visual inspection
│   └── 04_model_evaluation.ipynb             # ROC/PR curves, threshold tuning & feature importance
├── powerbi/
│   ├── measures.dax                          # 12 production DAX measures for KPIs & revenue risk
│   ├── README.md                             # Power BI setup guide
│   ├── relationships.md                      # 1-to-1 / 1-to-Many single-direction Star Schema rules
│   └── visual_mapping.md                     # 4-Page Power BI dashboard layout specification
├── reports/
│   ├── business_recommendations.md           # Prioritized retention roadmap & campaign ROI simulation
│   ├── data_quality_report.md                # Zero-tenure blank TotalCharges audit
│   ├── database_inspection.md                # SQLite table & index verification report
│   ├── findings.md                           # Full statistical and segment EDA report
│   └── model_evaluation.md                   # CV vs Held-out Test metrics, thresholds & odds ratios
├── sql/
│   ├── 01_schema.sql                         # DDL for customer_churn_raw, 5 B-tree indexes & vw_telco_cleaned
│   ├── 02_data_quality.sql                   # Primary key uniqueness & whitespace TotalCharges audit
│   ├── 03_customer_metrics.sql               # Executive customer & MRR exposure queries
│   ├── 04_churn_analysis.sql                 # Dimensional churn breakdowns
│   ├── 05_customer_segmentation.sql          # Lifecycle & contract cohort queries
│   ├── 06_advanced_analysis.sql              # Window functions & multi-factor risk ranking
│   └── README.md
├── src/
│   ├── __init__.py                           # Package initialization (v1.0.0)
│   ├── config.py                             # Pydantic BaseModel settings for DB, Paths, ML & Visuals
│   ├── database.py                           # DatabaseManager for SQLite & PostgreSQL execution
│   ├── inspect_data.py                       # Phase 1: Raw database ingestion & schema validation
│   ├── clean_data.py                         # Phase 2: Data cleaning & domain feature engineering
│   ├── eda.py                                # Phase 3: Segment aggregation & Charts 01-10 generation
│   ├── train_model.py                        # Phase 4: Scikit-learn pipeline training & 5-fold CV
│   ├── evaluate_model.py                     # Phase 5: Test evaluation, threshold curves & Charts 11-13
│   ├── predict_customers.py                  # Phase 6: Batch probability scoring & E[Loss] calculation
│   └── export_powerbi.py                     # Phase 7: Star-Schema CSV decomposition
├── tests/
│   ├── test_data_cleaning.py                 # Unit tests for imputation & feature engineering
│   ├── test_data_schema.py                   # Schema, row count (7,043) & primary key tests
│   ├── test_metrics.py                       # Cross-checks SQL KPIs against pandas calculations
│   └── test_predictions.py                   # Validates probability bounds [0,1] & risk tier mapping
├── visuals/                                  # 13 high-resolution 300-DPI PNG charts
├── customer_churn_dashboard.html             # Unified Interactive WebApp Dashboard (New Deliverable)
├── customer_churn_executive_dashboard.png    # Unified 9-Panel Static Dashboard (New Deliverable)
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## 3. Deep-Dive Codebase Analysis (`src/`, `sql/`, `powerbi/`, `tests/`)

### 3.1 Python Source Modules (`src/`)

| Module File | Pipeline Phase | Core Classes / Functions | Technical Implementation & Analytical Logic |
| :--- | :--- | :--- | :--- |
| `src/config.py` | Configuration | `DatabaseConfig`, `PathConfig`, `ModelConfig`, `VisConfig` | Built on `pydantic.BaseModel`. Centralizes environment variables (`DB_TYPE`, `SQLITE_DB_PATH`, PostgreSQL credentials), directory paths, ML constants (`random_seed=42`, `test_size=0.20`, `cv_folds=5`, `decision_threshold=0.32`), and visual theme (`#2b5c8f` primary blue, `#d95f02` accent orange, `300 DPI`). |
| `src/database.py` | DB Layer | `DatabaseManager`, `bootstrap_sqlite_from_csv()` | Wraps `sqlite3` (and PostgreSQL-compatible connection strings) with context-managed query execution (`execute_query` returning `pd.DataFrame` and `execute_script` for multi-statement `.sql` files). |
| `src/inspect_data.py` | Phase 1: Ingestion | `inspect_database()` | Queries `customer_churn_raw` to verify exact row count (`7,043`), column count (`21`), primary key uniqueness (`customerID`), and detects exactly **11 whitespace strings** (`" "`) in `TotalCharges` corresponding to new customers with `tenure == 0`. Outputs `reports/database_inspection.md`. |
| `src/clean_data.py` | Phase 2: Cleaning & Features | `clean_and_transform_churn_data()`, `assign_tenure_group()`, `assign_customer_segment()` | Replaces regex whitespace `r"^\s*$"` in `TotalCharges` with `NaN` and imputes `0.0`. Maps binary strings (`Yes`/`No`) to `1`/`0`. Engineers three high-signal features: `tenure_group` (`0-12m`, `13-24m`, `25-48m`, `49-72m`), `customer_segment` (`New Month-to-Month (<=12m)` / `High-Risk Newbie`, `Established Month-to-Month (>12m)` / `At-Risk Tenured`, `One-Year Contract`, `Two-Year Contract`), and `addon_services_count` (sum of 6 add-ons: `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`). |
| `src/eda.py` | Phase 3: Exploratory Analysis | `compute_eda_metrics()`, `summarize_group()` | Computes global benchmarks ($26.54\%$ churn rate, $\$456,116.60$ total MRR, $\$139,130.85$ churned MRR, $\$1,669,570.20$ annualized loss) and grouped aggregations (`Share_Pct`, `Churn_Rate_Pct`, `Churned_MRR_Share_Pct`), rendering **Visuals 01 through 10** into `visuals/`. |
| `src/train_model.py` | Phase 4: ML Training | `build_model_pipeline()`, `train_and_evaluate()` | Performs a stratified 80/20 train/test split ($5,634$ train / $1,409$ test). Constructs a leak-free `scikit-learn` `Pipeline` using `ColumnTransformer`: `StandardScaler()` on 4 numeric features (`tenure`, `MonthlyCharges`, `TotalCharges`, `addon_services_count`) and `OneHotEncoder(handle_unknown="ignore")` on 18 categorical features (yielding **47 total encoded features**). Evaluates Logistic Regression and Random Forest across 5-fold `StratifiedKFold` CV and serializes `models/churn_model_pipeline.pkl` + `models/training_metrics.json`. |
| `src/evaluate_model.py` | Phase 5: Evaluation & Tuning | `evaluate_thresholds()` | Scores the held-out test set ($N=1,409$), sweeps classification thresholds from `0.20` to `0.70` (computing `TP`, `FP`, `FN`, `TN`, `Precision`, `Recall`, `F1`), extracts Logistic Regression standardized log-odds coefficients and Random Forest Gini importances, generates **Visuals 11 through 13**, and writes `reports/model_evaluation.md`. |
| `src/predict_customers.py` | Phase 6: Batch Scoring | `assign_risk_tier()`, `predict_customer_churn()` | Runs batch inference across all $7,043$ customers. Assigns `Churn_Probability`, maps risk tiers (`High Risk` $\ge 0.60$, `Medium Risk` $0.35\text{–}0.59$ [or $0.30\text{–}0.60$], `Low Risk` $< 0.35$), and computes customer-level `Expected_Monthly_Revenue_Loss = MonthlyCharges * Churn_Probability`. Exports `data/predictions/customer_risk_predictions.csv`. |
| `src/export_powerbi.py` | Phase 7: BI Export | `export_star_schema()` | Decomposes the scored dataframe into 1 Fact table (`Fact_Customer_Churn.csv`), 3 Dimension tables (`Dim_Customer_Profile.csv`, `Dim_Service_Subscription.csv`, `Dim_Billing_Contract.csv`), and 1 pre-aggregated cohort table (`Summary_Segment_KPIs.csv`) for zero-ambiguity Power BI modeling. |

### 3.2 Production SQL Layer (`sql/`)

1. **`sql/01_schema.sql`:** Defines `customer_churn_raw` with `customerID TEXT PRIMARY KEY`, creates 5 B-tree performance indexes (`idx_contract`, `idx_internet`, `idx_payment`, `idx_churn`, `idx_tenure`), and builds the clean analytical view `vw_telco_cleaned` which coerces blank `TotalCharges` to `0.0` via `CASE WHEN TotalCharges IS NULL OR TRIM(CAST(TotalCharges AS TEXT)) = '' THEN 0.0 ELSE CAST(TotalCharges AS REAL) END` and exposes `Churn_Binary`.
2. **`sql/02_data_quality.sql`:** Audits primary key duplicates (`GROUP BY customerID HAVING COUNT(*) > 1` $\rightarrow$ 0 rows) and isolates the 11 zero-tenure records with blank `TotalCharges`.
3. **`sql/03_customer_metrics.sql`:** Computes executive KPIs directly in SQL (`total_customers = 7043`, `churned_customers = 1869`, `overall_churn_rate_pct = 26.54`, `total_monthly_recurring_revenue_usd = 456116.60`, `churned_monthly_revenue_exposure_usd = 139130.85`, `mrr_exposure_pct = 30.50`).
4. **`sql/04_churn_analysis.sql` – `sql/06_advanced_analysis.sql`:** Executes dimensional groupings by Contract, Tenure Cohort, Internet Service, Payment Method, and Security/Tech Support bundles, plus window-function revenue risk rankings.

### 3.3 Automated Test Suite (`tests/` & `.github/workflows/tests.yml`)

* **`tests/test_data_cleaning.py`:** Verifies zero `NaN` values after `clean_and_transform_churn_data()`, confirms all 11 zero-tenure rows have `TotalCharges == 0.0`, and validates exact bucket boundaries for `tenure_group` and `customer_segment`.
* **`tests/test_data_schema.py`:** Asserts $7,043$ rows, unique `customerID` primary keys, and schema alignment with `data_dictionary.csv`.
* **`tests/test_metrics.py`:** Cross-validates SQL query outputs from `03_customer_metrics.sql` against `src/eda.py` pandas aggregations to guarantee zero metric drift.
* **`tests/test_predictions.py`:** Confirms `customer_risk_predictions.csv` contains all $7,043$ customers with probabilities strictly within $[0.0, 1.0]$ and valid risk tier labels.

## 4. Chart-by-Chart Analysis of All 13 Repository Visualizations (`visuals/`)

### Chart 01: `visuals/01_overall_churn_rate.png` — Overall Customer Churn vs. Retained Split
* **Visual Type & Generator:** Donut & Executive Proportion Chart (`src/eda.py`).
* **Exact Data Breakdown:**
  * **Retained Customers ($Churn = \text{No}$):** `5,174` customers (`73.46%` of base) | Retained MRR: `$316,985.75` (`69.50%` of total MRR).
  * **Churned Customers ($Churn = \text{Yes}$):** `1,869` customers (`26.54%` of base) | Churned MRR: `$139,130.85` (`30.50%` of total MRR).
* **Analytical Insight:** Revenue churn (`30.50%`) outpaces logo churn (`26.54%`) by **+396 bps** because churning customers carry a **21.5% higher average monthly bill** (`$74.44` vs. `$61.27` for retained customers).

### Chart 02: `visuals/02_churn_by_contract.png` — Churn Rate & Revenue Exposure by Contract Type
* **Visual Type & Generator:** Clustered Bar Chart (`src/eda.py`).
* **Exact Data Breakdown:**

| Contract Type | Customers | Customer Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Month-to-month** | 3,875 | 55.02% | 1,655 | 2,220 | **42.71%** | 18.04 | $66.40 | $257,294.15 | **$120,847.10** | **86.86%** |
| **One year** | 1,473 | 20.91% | 166 | 1,307 | **11.27%** | 42.04 | $65.05 | $95,816.60 | **$14,118.45** | **10.15%** |
| **Two year** | 1,695 | 24.07% | 48 | 1,647 | **2.83%** | 56.74 | $60.77 | $103,005.85 | **$4,165.30** | **2.99%** |

* **Analytical Insight:** Contract structure is the single strongest structural determinant of churn. Month-to-month subscribers represent `55.02%` of the customer base but generate **88.55% of all churned accounts** (`1,655 / 1,869`) and **86.86% of all lost MRR** (`$120,847.10 / $139,130.85`). Upgrading a customer from Month-to-month to a One-Year contract reduces churn risk by **3.8x** (`42.71%` $\rightarrow$ `11.27%`), and to a Two-Year contract by **15.1x** (`42.71%` $\rightarrow$ `2.83%`).

### Chart 03: `visuals/03_churn_by_tenure_group.png` — Churn Rate Across Customer Tenure Cohorts
* **Visual Type & Generator:** Cohort Bar & Line Combo Chart (`src/eda.py`).
* **Exact Data Breakdown:**

| Tenure Cohort (`tenure_group`) | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Churned MRR Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0–12 Months** | 2,186 | 31.04% | 1,037 | 1,149 | **47.44%** | 4.73 | $56.10 | $122,629.75 | **$68,954.25** | **49.56%** |
| **13–24 Months** | 1,024 | 14.54% | 294 | 730 | **28.71%** | 18.35 | $61.36 | $62,829.85 | **$23,081.65** | **16.59%** |
| **25–48 Months** | 1,594 | 22.63% | 325 | 1,269 | **20.39%** | 36.19 | $65.93 | $105,093.30 | **$27,462.50** | **19.74%** |
| **49–72 Months** | 2,239 | 31.79% | 213 | 2,026 | **9.51%** | 63.05 | $73.95 | $165,563.70 | **$19,632.45** | **14.11%** |

* **Analytical Insight:** Almost half (**47.44%**) of all first-year subscribers leave within their first 12 months, accounting for **49.56% ($68,954.25)** of total monthly revenue loss. Once a customer survives past 24 months, overall retention across `25–72 Months` (`3,833` customers) reaches **86.0%** (`538` churned vs. `3,295` retained), even though long-tenured customers pay higher monthly bills (`$73.95` in `49–72 Months` vs. `$56.10` in `0–12 Months`).

### Chart 04: `visuals/04_churn_by_payment_method.png` — Payment Method Friction Analysis
* **Visual Type & Generator:** Horizontal Comparison Bar Chart (`src/eda.py`).
* **Exact Data Breakdown:**

| Payment Method | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Churned MRR Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Electronic check** | 2,365 | 33.58% | 1,071 | 1,294 | **45.29%** | 25.17 | $76.26 | $180,345.00 | **$84,288.75** | **60.58%** |
| **Mailed check** | 1,612 | 22.89% | 308 | 1,304 | **19.11%** | 21.83 | $43.92 | $70,794.30 | **$16,803.60** | **12.08%** |
| **Bank transfer (automatic)** | 1,544 | 21.92% | 258 | 1,286 | **16.71%** | 43.66 | $67.19 | $103,745.45 | **$20,673.10** | **14.86%** |
| **Credit card (automatic)** | 1,522 | 21.61% | 232 | 1,290 | **15.24%** | 43.27 | $66.51 | $101,231.85 | **$17,365.40** | **12.48%** |

* **Analytical Insight:** Customers paying manually via **Electronic check** churn at **45.29%** (`1,071` churners) and account for **60.58% ($84,288.75)** of all churned MRR. Because manual electronic billing forces a monthly active payment decision on high-bill accounts (`$76.26` avg charge), it creates recurring friction compared to passive **Bank Transfer (`16.71%`)** and **Credit Card (`15.24%`)** auto-pay methods.

### Chart 05: `visuals/05_churn_by_internet_service.png` — Internet Service Tier Breakdown
* **Visual Type & Generator:** Grouped Bar & Donut Chart (`src/eda.py`).
* **Exact Data Breakdown:**

| Internet Service Tier | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Churned MRR Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fiber optic** | 3,096 | 43.96% | 1,297 | 1,799 | **41.89%** | 32.92 | **$91.50** | $283,284.40 | **$114,300.05** | **82.15%** |
| **DSL** | 2,421 | 34.37% | 459 | 1,962 | **18.96%** | 32.82 | **$58.10** | $140,665.35 | **$22,529.20** | **16.19%** |
| **No Internet** | 1,526 | 21.67% | 113 | 1,413 | **7.40%** | 30.55 | **$21.08** | $32,166.85 | **$2,301.60** | **1.65%** |

* **Analytical Insight:** Although Fiber Optic subscribers have virtually the same average tenure (`32.92` months) as DSL subscribers (`32.82` months), their churn rate is **2.21x higher** (`41.89%` vs. `18.96%`). Combined with an average bill of `$91.50/month`, Fiber Optic accounts represent **82.15% ($114,300.05/month)** of the company's total revenue loss—pointing to price sensitivity and unbundled support gaps on premium tiers.

### Chart 06: `visuals/06_monthly_charges_by_churn.png` — Monthly Charges KDE Distribution by Churn
* **Visual Type & Generator:** Kernel Density Estimate (KDE) & Box Distribution Plot (`src/eda.py`).
* **Exact Statistical Profile:**
  * **All Customers ($N=7,043$):** Mean = `$64.76` | Median = `$70.35`.
  * **Retained Customers ($n=5,174$):** Mean = `$61.27` | Median = `$64.43` (Bimodal distribution with a large spike around `$19–$25` for voice-only/basic plans and a broader plateau across `$45–$85`).
  * **Churned Customers ($n=1,869$):** Mean = `$74.44` | Median = `$79.65` (Unimodal concentration heavily skewed between **`$70.00` and `$105.00`**).
* **Analytical Insight:** The `+$15.22` median gap (`$79.65` vs. `$64.43`) demonstrates that churn is concentrated among high-ARPU Fiber Optic customers rather than entry-level plans.

### Chart 07: `visuals/07_tenure_distribution_by_churn.png` — Customer Tenure KDE Distribution by Churn
* **Visual Type & Generator:** Kernel Density Estimate (KDE) & Histogram Distribution (`src/eda.py`).
* **Exact Statistical Profile:**
  * **All Customers ($N=7,043$):** Mean = `32.37 months` | Median = `29.0 months`.
  * **Churned Customers ($n=1,869$):** Mean = `17.98 months` | Median = **`10.0 months`** (Steep exponential decay from Month 1; `55.5%` of all churn occurs within the first 12 months).
  * **Retained Customers ($n=5,174$):** Mean = `37.57 months` | Median = **`38.0 months`** (U-shaped / late-peaking distribution with a massive loyalty cluster at `65–72 months`).
* **Analytical Insight:** The 28-month median tenure gap (`10.0m` vs. `38.0m`) confirms that early onboarding failure in months 1–6 is the primary lifecycle vulnerability.

### Chart 08: `visuals/08_churn_by_customer_segment.png` — Churn Across Engineered Lifecycle Segments
* **Visual Type & Generator:** Horizontal Segment Bar Chart (`src/eda.py` & `src/clean_data.py`).
* **Exact Data Breakdown:**

| Engineered Customer Segment | Code Label (`clean_data.py`) | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Churned MRR Share (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **New Month-to-Month ($\le 12\text{m}$)** | `High-Risk Newbie` | 1,994 | 28.31% | 1,024 | 970 | **51.35%** | 4.47 | $58.22 | $116,086.50 | **$68,079.55** | **48.93%** |
| **Established Month-to-Month ($>12\text{m}$)** | `At-Risk Tenured` | 1,881 | 26.71% | 631 | 1,250 | **33.55%** | 32.41 | $75.07 | $141,207.65 | **$52,767.55** | **37.93%** |
| **One-Year Contract** | `Stable One-Year` | 1,473 | 20.91% | 166 | 1,307 | **11.27%** | 42.04 | $65.05 | $95,816.60 | **$14,118.45** | **10.15%** |
| **Two-Year Contract** | `Loyal Two-Year` | 1,695 | 24.07% | 48 | 1,647 | **2.83%** | 56.74 | $60.77 | $103,005.85 | **$4,165.30** | **2.99%** |

* **Analytical Insight:** Splitting Month-to-month customers at the 12-month boundary uncovers two distinct operational personas:
  1. **New Month-to-Month (`High-Risk Newbie`, $n=1,994$):** Over half (**51.35%**) churn at an average tenure of just `4.47 months`, requiring immediate onboarding intervention.
  2. **Established Month-to-Month (`At-Risk Tenured`, $n=1,881$):** Despite staying an average of `32.41 months`, they pay the highest average monthly rate (`$75.07`) and still churn at **33.55%** (`$52,767.55` MRR lost), making them prime candidates for contract lock-in incentives.

### Chart 09: `visuals/09_churn_by_security_tech_support.png` — Security & Tech Support Add-on Impact
* **Visual Type & Generator:** Grouped Add-On Impact Bar Chart (`src/eda.py`).
* **Exact Data Breakdown (Internet Subscribers):**

| Service Add-On Status | Customers | Share of Total Base (%) | Churned Customers | Churn Rate (%) | Churned MRR ($) | Share of Total Churned MRR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **OnlineSecurity = No** | 3,498 | 49.67% | 1,461 | **41.77%** | **$112,762.75** | **81.05%** |
| **OnlineSecurity = Yes** | 2,019 | 28.67% | 295 | **14.61%** | **$24,066.50** | **17.30%** |
| **TechSupport = No** | 3,473 | 49.31% | 1,446 | **41.64%** | **$110,709.80** | **79.57%** |
| **TechSupport = Yes** | 2,044 | 29.02% | 310 | **15.17%** | **$26,119.45** | **18.77%** |
| **No Internet Service** | 1,526 | 21.67% | 113 | **7.40%** | **$2,301.60** | **1.65%** |

* **Analytical Insight:** Value-added protection services create strong ecosystem lock-in. Customers with `OnlineSecurity = Yes` churn at **14.61%** vs. **41.77%** without it (**-27.16 percentage points**), while `TechSupport = Yes` reduces churn from **41.64%** to **15.17%** (**-26.47 percentage points**). Over **80% of all churned MRR** originates from accounts lacking Online Security (`81.05%`) or Tech Support (`79.57%`).

### Chart 10: `visuals/10_contract_tenure_churn_heatmap.png` — Contract $\times$ Tenure Cohort Churn Heatmap
* **Visual Type & Generator:** 2D Annotated Cohort Matrix Heatmap (`src/eda.py`).
* **Exact Cross-Tabulated Churn Rates (% and Cohort Sizes):**

| Contract Type \ Tenure Cohort | `0–12 Months` | `13–24 Months` | `25–48 Months` | `49–72 Months` | Row Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Month-to-month** | **51.35%** ($1,024 / 1,994$) | **37.72%** ($278 / 737$) | **32.92%** ($264 / 802$) | **26.02%** ($89 / 342$) | **42.71%** ($1,655 / 3,875$) |
| **One year** | **10.68%** ($13 / 122$) | **8.12%** ($16 / 197$) | **10.62%** ($55 / 518$) | **12.93%** ($82 / 636$) | **11.27%** ($166 / 1,473$) |
| **Two year** | **0.00%** ($0 / 70$) | **0.00%** ($0 / 90$) | **2.19%** ($6 / 274$) | **3.32%** ($42 / 1,261$) | **2.83%** ($48 / 1,695$) |
| **Column Total** | **47.44%** ($1,037 / 2,186$) | **28.71%** ($294 / 1,024$) | **20.39%** ($325 / 1,594$) | **9.51%** ($213 / 2,239$) | **26.54%** ($1,869 / 7,043$) |

* **Analytical Insight:** The heatmap proves that **Contract Type dominates Tenure** even at long tenures: a Month-to-month subscriber who has been with the company for `49–72 Months` still churns at **26.02%**, which is **2.4x higher** than a first-year One-Year contract subscriber (**10.68%**). Meanwhile, Two-Year contracts experience **0.00% churn** during the first 24 months.

### Chart 11: `visuals/11_model_roc_pr_curves.png` — Comparative ROC & Precision-Recall Curves
* **Visual Type & Generator:** Dual-Panel ROC Curve & Precision-Recall Curve (`src/evaluate_model.py`).
* **Exact Cross-Validation & Held-Out Test Benchmarks:**

| Evaluation Split & Model | ROC-AUC | PR-AUC | Accuracy | Precision | Recall | Specificity | F1-Score | Confusion Matrix (`TP / FP / FN / TN`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5-Fold CV (`n=5,634`) — Logistic Regression** | `0.8424 ± 0.0056` | `0.6497 ± 0.0123` | `80.26% ± 0.58%` | `65.30% ± 0.92%` | `54.65% ± 2.89%` | — | `59.47% ± 1.95%` | 5-Fold Stratified Mean ± SD |
| **5-Fold CV (`n=5,634`) — Random Forest** | `0.8432 ± 0.0086` | `0.6599 ± 0.0141` | `79.82% ± 0.77%` | `66.16% ± 1.58%` | `49.10% ± 5.03%` | — | `56.24% ± 3.35%` | 5-Fold Stratified Mean ± SD |
| **Held-Out Test (`N=1,409`) — Logistic Regression** | **0.8575** | **0.6843** | **81.33%** | **69.07%** | **53.74%** | **91.30%** | **60.45%** | `TP=201, FP=90, FN=173, TN=945` |
| **Held-Out Test (`N=1,409`) — Random Forest** | **0.8651** | **0.6869** | **80.84%** | **69.70%** | **49.20%** | **92.27%** | **57.68%** | `TP=184, FP=80, FN=190, TN=955` |

* **Analytical Insight:** Both pipelines show zero overfitting between 5-fold cross-validation and the 20% held-out test set. While Random Forest achieves a slightly higher test ROC-AUC (`0.8651` vs `0.8575`), **Logistic Regression** achieves higher test Recall (`53.74%` vs `49.20%`), higher F1-Score (`60.45%` vs `57.68%`), higher Accuracy (`81.33%` vs `80.84%`), and well-calibrated probabilities for Expected Monthly Revenue Loss ($\text{MRR} \times P(\text{Churn})$).

### Chart 12: `visuals/12_threshold_optimization.png` — Precision, Recall & F1 Decision Threshold Curve
* **Visual Type & Generator:** Multi-Metric Threshold Sweep & ROI Trade-Off Curve (`src/evaluate_model.py`).
* **Complete Test Set Threshold Table ($N = 1,409$, Actual Churners = $374$):**

| Decision Threshold | Flagged Customers | Flagged Share (%) | True Positives (`TP`) | False Positives (`FP`) | False Negatives (`FN`) | True Negatives (`TN`) | Precision (%) | Recall (%) | F1-Score (%) | Simulated Net Campaign Benefit ($)* |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.20** | 694 | 49.3% | 332 | 362 | 42 | 673 | 47.84% | **88.77%** | 62.17% | +$32,450 |
| **0.25 (ROI Peak)** | 602 | 42.7% | 312 | 290 | 62 | 745 | 51.83% | **83.42%** | 63.93% | **+$31,750 / +$33,625** |
| **0.30 (F1 Peak)** | 525 | 37.3% | 293 | 232 | 81 | 803 | 55.81% | **78.34%** | **65.18%** | +$30,825 |
| **0.32 (Config Default)** | ~498 | ~35.3% | ~282 | ~216 | ~92 | ~819 | ~56.63% | **75.40%** | ~64.68% | +$29,850 |
| **0.35** | 460 | 32.6% | 268 | 192 | 106 | 843 | 58.26% | **71.66%** | 64.27% | +$28,700 |
| **0.40** | 400 | 28.4% | 246 | 154 | 128 | 881 | 61.50% | 65.78% | 63.57% | +$26,900 |
| **0.45** | 341 | 24.2% | 218 | 123 | 156 | 912 | 63.93% | 58.29% | 60.98% | +$24,175 |
| **0.50 (Std Default)** | 291 | 20.7% | 201 | 90 | 173 | 945 | 69.07% | 53.74% | 60.45% | +$22,875 |
| **0.55** | 240 | 17.0% | 176 | 64 | 198 | 971 | 73.33% | 47.06% | 57.33% | +$20,400 |
| **0.60** | 187 | 13.3% | 145 | 42 | 229 | 993 | 77.54% | 38.77% | 51.69% | +$17,075 |
| **0.70** | 81 | 5.7% | 66 | 15 | 308 | 1020 | **81.48%** | 17.65% | 29.01% | +$7,875 |

*\*Note: Campaign ROI simulation assumes $\$25$ incentive/outreach cost per flagged customer (`TP + FP`) and $\$150$ expected retention value per caught churner (`TP`), yielding $\$125 \times \text{TP} - \$25 \times \text{FP}$.*

* **Analytical Insight:** Operating at the standard `0.50` threshold misses **46.26% of all churning customers** (`173` False Negatives). Shifting the operational cut-off to **`0.30–0.32`** maximizes the F1-Score (`65.18%`) and captures **3 out of every 4 churners (`75.40%–78.34%` recall)**, while lowering to **`0.25`** maximizes net retention profit (**+$33,625**, a **+47.0% net gain** over `0.50`).

### Chart 13: `visuals/13_feature_importance_top15.png` — Top Predictive Features (Gini & Log-Odds)
* **Visual Type & Generator:** Horizontal Feature Importance Bar Chart (`src/evaluate_model.py`).
* **Dual-Model Feature Importance Comparison:**

| Rank | Random Forest Feature | RF Gini Importance (%) | Logistic Regression Feature | Standardized Coeff ($\beta$) | Odds Ratio ($e^\beta$) | Directional Impact on Churn |
| :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| **1** | `tenure` | **15.40%** | `tenure` | **-1.4941** | `0.224x` | Strongest Retention Driver (Reduces Risk) |
| **2** | `Contract_Month-to-month` | **13.12%** | `TotalCharges` | **+0.7085** | `2.031x` | Cumulative Billing Exposure (Increases Risk) |
| **3** | `OnlineSecurity_No` | **8.47%** | `Contract_Two year` | **-0.6692** | `0.512x` | Long-Term Contract Lock-In (Reduces Risk) |
| **4** | `TotalCharges` | **8.01%** | `Contract_Month-to-month` | **+0.6298** | `1.877x` | No-Commitment Vulnerability (Increases Risk) |
| **5** | `TechSupport_No` | **7.40%** | `InternetService_Fiber optic` | **+0.6006** | `1.823x` | Premium Tier Price/Service Risk (Increases Risk) |
| **6** | `InternetService_Fiber optic` | **6.39%** | `InternetService_DSL` | **-0.4662** | `0.627x` | Lower-Cost Internet Stability (Reduces Risk) |
| **7** | `Contract_Two year` | **4.93%** | `MonthlyCharges` | **-0.3834** | `0.682x` | Collinear Adjustment vs Tier/TotalCharges |
| **8** | `PaymentMethod_Electronic check` | **4.55%** | `TechSupport_No` | **+0.2521** | `1.287x` | Missing Technical Support (Increases Risk) |
| **9** | `MonthlyCharges` | **4.37%** | `PaymentMethod_Electronic check` | **+0.2485** | `1.282x` | Manual Payment Friction (Increases Risk) |
| **10** | `InternetService_DSL` | **3.04%** | `OnlineSecurity_No` | **+0.2219** | `1.248x` | Missing Security Bundle (Increases Risk) |

* **Analytical Insight:** Both parametric (Logistic Regression) and non-parametric tree-based (Random Forest) models converge on the exact same top business drivers: **Tenure**, **Month-to-Month vs. Two-Year Contracts**, **Fiber Optic Service**, **Missing Online Security / Tech Support**, and **Electronic Check Payment**.

## 5. Power BI Star-Schema Architecture & DAX Specification (`powerbi/`)

### 5.1 Normalized Star Schema (`data/processed/powerbi/`)

```text
                  +----------------------------------+
                  |       Dim_Customer_Profile       |
                  |----------------------------------|
                  | PK customerID                    |
                  |    gender, SeniorCitizen,        |
                  |    Senior_Label, Partner,        |
                  |    Dependents, Tenure_Group      |
                  +-----------------+----------------+
                                    | 1
                                    | (Single Filter)
                                    v 1
+-----------------------------------+-----------------------------------+
|                         Fact_Customer_Churn                           |
|-----------------------------------------------------------------------|
| PK customerID                                                         |
|    tenure, MonthlyCharges, TotalCharges, Total_Services_Count,        |
|    Churn_Flag (Churn_Binary), Churn_Probability,                      |
|    Predicted_Risk_Tier, Expected_Monthly_Revenue_Loss                 |
+-----------------+-----------------------------------+-----------------+
                  ^ 1                                 ^ 1
                  | (Single Filter)                   | (Single Filter)
                  | 1                                 | 1
+-----------------+----------------+ +----------------+-----------------+
|     Dim_Service_Subscription     | |       Dim_Billing_Contract       |
|----------------------------------| |----------------------------------|
| PK customerID                    | | PK customerID                    |
|    PhoneService, MultipleLines,  | |    Contract, PaperlessBilling,   |
|    InternetService, 6 Add-Ons,   | |    PaymentMethod                 |
|    Has_Tech_Support_Bundle       | +----------------------------------+
+----------------------------------+
```

### 5.2 Complete Pre-Aggregated Cohort Table (`Summary_Segment_KPIs.csv`)

Below is the complete 20-cohort breakdown exported by `src/export_powerbi.py` (sorted by Expected Monthly Revenue Loss):

| Lifecycle Segment | Contract | Internet | Risk Tier | Customers | Churned | Churn Rate (%) | Total MRR ($) | Churned MRR ($) | Expected Monthly Loss ($) | Avg Churn Prob (%) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | Fiber optic | **High Risk** | 676 | 535 | **79.14%** | $55,784.80 | $44,349.25 | **$39,576.96** | **70.94%** |
| **Established Month-to-Month ($>12\text{m}$)** | Month-to-month | Fiber optic | **Medium Risk** | 806 | 414 | **51.36%** | $72,251.40 | $37,448.10 | **$33,783.81** | **46.80%** |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | Fiber optic | **Medium Risk** | 240 | 108 | **45.00%** | $19,398.35 | $8,829.05 | **$10,384.69** | **53.53%** |
| **One-Year Contract** | One year | Fiber optic | **Low Risk** | 531 | 100 | **18.83%** | $52,455.10 | $10,163.90 | **$10,204.93** | **19.27%** |
| **Established Month-to-Month ($>12\text{m}$)** | Month-to-month | Fiber optic | **Low Risk** | 340 | 57 | **16.76%** | $31,564.95 | $5,372.75 | **$8,950.01** | **28.35%** |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | DSL | **Medium Risk** | 391 | 204 | **52.17%** | $17,709.35 | $9,281.10 | **$8,222.80** | **46.67%** |
| **Established Month-to-Month ($>12\text{m}$)** | Month-to-month | DSL | **Low Risk** | 509 | 86 | **16.90%** | $27,429.50 | $4,411.65 | **$5,501.79** | **20.67%** |
| **Two-Year Contract** | Two year | Fiber optic | **Low Risk** | 429 | 31 | **7.23%** | $44,861.15 | $3,246.10 | **$4,250.14** | **9.49%** |
| **Established Month-to-Month ($>12\text{m}$)** | Month-to-month | Fiber optic | **High Risk** | 66 | 48 | **72.73%** | $6,181.60 | $4,482.85 | **$3,871.14** | **62.59%** |
| **One-Year Contract** | One year | DSL | **Low Risk** | 570 | 53 | **9.30%** | $34,996.15 | $3,356.25 | **$3,781.22** | **10.74%** |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | DSL | **Low Risk** | 256 | 51 | **19.92%** | $13,871.95 | $2,751.65 | **$3,741.19** | **27.29%** |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | No | **Low Risk** | 367 | 73 | **19.89%** | $7,442.25 | $1,469.70 | **$1,518.83** | **20.46%** |
| **Two-Year Contract** | Two year | DSL | **Low Risk** | 628 | 12 | **1.91%** | $44,250.75 | $805.70 | **$1,384.58** | **3.29%** |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | DSL | **High Risk** | 43 | 38 | **88.37%** | $1,458.40 | $1,319.15 | **$973.22** | **66.88%** |
| **Established Month-to-Month ($>12\text{m}$)** | Month-to-month | DSL | **Medium Risk** | 24 | 15 | **62.50%** | $949.25 | $603.70 | **$363.27** | **38.32%** |
| **One-Year Contract** | One year | Fiber optic | **Medium Risk** | 8 | 4 | **50.00%** | $787.05 | $408.05 | **$304.15** | **38.53%** |
| **Established Month-to-Month ($>12\text{m}$)** | Month-to-month | No | **Low Risk** | 136 | 11 | **8.09%** | $2,830.95 | $226.60 | **$289.19** | **10.25%** |
| **One-Year Contract** | One year | No | **Low Risk** | 364 | 9 | **2.47%** | $7,578.30 | $190.25 | **$218.81** | **2.86%** |
| **Two-Year Contract** | Two year | No | **Low Risk** | 638 | 5 | **0.78%** | $13,893.95 | $113.50 | **$161.00** | **1.11%** |
| **New Month-to-Month ($\le 12\text{m}$)** | Month-to-month | No | **Medium Risk** | 21 | 15 | **71.43%** | $421.40 | $301.55 | **$156.65** | **37.17%** |

## 6. Strategic Retention Roadmap & Quantified Business Recommendations

| Priority | Strategic Initiative | Target Customer Segment | Quantified Empirical Evidence | Recommended Action & Expected Financial Impact |
| :---: | :--- | :--- | :--- | :--- |
| **Priority 1** | **Month-to-Month $\rightarrow$ 1-Year Contract Migration** | **3,875** Month-to-month subscribers (`55.02%` of base), prioritizing Fiber Optic users in months 3–12 | Month-to-month churn is **42.71%** (`1,655` churners) and represents **$120,847.10/mo (86.86%)** of all churned MRR | Offer a 1-month bill credit or **$10/mo loyalty discount** upon upgrading to a 12-month contract at the 90-day mark; converting 20% of High/Medium risk M2M users protects **~$24.1K MRR ($289K/yr)**. |
| **Priority 2** | **Fiber Optic "Tech Support & Security" Bundle** | **1,859** Fiber Optic subscribers lacking `OnlineSecurity` and `TechSupport` | Fiber Optic churn is **41.89%** (`$114,300.05` MRR lost); missing security/support drives **41.77% / 41.64%** churn vs **14.61% / 15.17%** with add-ons | Bundle complimentary **6-month Online Security + Tech Support** into Fiber Optic onboarding to increase ecosystem stickiness and cut cohort churn by up to **64%**. |
| **Priority 3** | **Electronic Check $\rightarrow$ Auto-Pay Conversion** | **2,365** Electronic check payers (`33.58%` of base) | Electronic check users churn at **45.29%** (`1,071` churners; **$84,288.75 MRR**, `60.58%` of total loss) vs **15.24%–16.71%** on Auto-Pay | Trigger in-app/email billing prompts offering a **$5/mo Auto-Pay discount** or one-time **$15 credit** for switching to Credit Card or Bank Transfer auto-pay. |
| **Priority 4** | **First-Year (0–12m) Proactive Onboarding Cadence** | **2,186** First-year subscribers (`31.04%` of base), especially the **676 High-Risk New M2M Fiber** cohort (`79.14%` actual churn) | First-year churn peaks at **47.44%** (`1,037` churners; **$68,954.25 MRR**, `49.56%` of total loss) with median churn tenure at **10.0 months** | Automate Day 15, Day 45, and Day 90 onboarding health checks for all accounts with `Churn_Probability >= 0.30` (or `0.25`), delivering **+$30,825 to +$33,625** in net retention benefit per 1,409 customers. |

## 7. Quickstart & Execution Instructions

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/turbodeva64-spec/customer-churn-intelligence.git
cd customer-churn-intelligence
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Full 7-Phase Pipeline
```bash
python src/inspect_data.py       # Phase 1: Ingest raw data to SQLite & audit schema
python src/clean_data.py         # Phase 2: Impute TotalCharges & engineer features
python src/eda.py                # Phase 3: Compute KPIs & export Charts 01-10
python src/train_model.py        # Phase 4: Train LogReg & Random Forest (5-fold CV)
python src/evaluate_model.py     # Phase 5: Evaluate test set, thresholds & Charts 11-13
python src/predict_customers.py  # Phase 6: Score all 7,043 customers & compute E[Loss]
python src/export_powerbi.py     # Phase 7: Export 5 Star-Schema CSVs for Power BI
```

### 3. Run Automated Pytest Verification
```bash
pytest tests/
```

## License

This project is licensed under the MIT License — see the [LICENSE](https://www.google.com/search?q=https://github.com/turbodeva64-spec/customer-churn-intelligence/blob/main/LICENSE) file for details.

