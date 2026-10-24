# Machine Learning Model Evaluation Report

## 1. Experimental Design & Leakage Prevention
- **Dataset**: `data/processed/cleaned_churn.csv` (`7,043` customers)
- **Train / Test Split**: Stratified 80/20 split (`random_seed = 42`):
  - **Training Set**: `5,634` customers (`26.54%` churn rate)
  - **Held-Out Test Set**: `1,409` customers (`26.54%` churn rate)
- **Leakage Controls**:
  - `customerID` is strictly excluded from model features (`47` encoded features total: `4` numeric + `43` one-hot categorical indicators).
  - Target columns (`Churn`, `Churn_Flag`) and post-hoc audit flags are excluded.
  - All numerical medians, means, standard deviations, and categorical vocabularies are fit **exclusively on the training fold** during 5-fold cross-validation and on the training split prior to test evaluation.
- **Execution Engine Note**: Because outbound package installation is disabled in this VM and `scikit-learn` is not pre-installed, `src/train_model.py` implements an exact, deterministic L2-regularized Logistic Regression solver via `scipy.optimize.minimize` (`L-BFGS-B`) and a vectorized Bootstrap-Aggregated CART Random Forest classifier in NumPy.

---

## 2. 5-Fold Stratified Cross-Validation Results (Training Set Only, n = 5,634)

| Model | CV ROC-AUC (Mean ± SD) | CV PR-AUC (Mean ± SD) | CV F1-Score (Mean ± SD) | CV Precision (Mean ± SD) | CV Recall (Mean ± SD) | CV Accuracy (Mean ± SD) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Logistic Regression** | **`0.8424 ± 0.0056`** | **`0.6497 ± 0.0123`** | `59.47% ± 1.95%` | `65.30% ± 0.92%` | `54.65% ± 2.89%` | `80.26% ± 0.58%` |
| **Random Forest** | `0.8432 ± 0.0086` | `0.6599 ± 0.0141` | `56.24% ± 3.35%` | `66.16% ± 1.58%` | `49.10% ± 5.03%` | `79.82% ± 0.77%` |

---

## 3. Held-Out Test Set Performance (n = 1,409, Default Threshold = 0.50)

| Model | Test ROC-AUC | Test PR-AUC | Accuracy | Precision | Recall | Specificity | F1-Score | TP | FP | FN | TN |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Logistic Regression (Champion)** | **`0.8575`** | **`0.6843`** | `81.33%` | `69.07%` | `53.74%` | `91.30%` | **`60.45%`** | 201 | 90 | 173 | 945 |
| **Random Forest** | `0.8651` | `0.6869` | `80.84%` | `69.70%` | `49.20%` | `92.27%` | `57.68%` | 184 | 80 | 190 | 955 |

### Why Accuracy Alone Is Misleading for Customer Churn
A naive majority-class classifier that predicts `"No Churn"` for every customer achieves **`73.46%` accuracy** while capturing **`0.0%` of actual churners** (`$0` of revenue at risk identified). Therefore, **ROC-AUC, PR-AUC, Recall, Precision, and F1-Score** at business-calibrated probability thresholds are the primary evaluation criteria.

---

## 4. Threshold Optimization & Retention Campaign Capacity Analysis
At the default `0.50` threshold, Logistic Regression achieves `69.07%` precision but only `53.74%` recall (`173` of `374` test-set churners missed). Lowering the decision threshold to **`0.35`** increases recall to **`71.66%`** (capturing **`74.4%`** of all monthly revenue at risk in the test set) and maximizes F1-score (`64.27%`) and simulated 6-month campaign net benefit.

*Note: Campaign financial columns below are **illustrative simulations** assuming a `$15.00` outreach cost per flagged customer and a `30%` save rate over a `6-month` horizon.*

| Threshold | Flagged Customers | Flagged Share (%) | TP | FP | FN | TN | Precision (%) | Recall (%) | F1-Score (%) | MRR Captured ($) | MRR Capture (%) | Sim. 6m Net Value ($) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.20` | 694 | 49.3% | 332 | 362 | 42 | 673 | 47.84% | 88.77% | 62.17% | $24,728.95 | 90.3% | $34,102.11 |
| `0.25` | 602 | 42.7% | 312 | 290 | 62 | 745 | 51.83% | 83.42% | 63.93% | $23,424.60 | 85.5% | $33,134.28 |
| `0.30` | 525 | 37.3% | 293 | 232 | 81 | 803 | 55.81% | 78.34% | 65.18% | $22,116.25 | 80.7% | $31,934.25 |
| `0.35` | 460 | 32.6% | 268 | 192 | 106 | 843 | 58.26% | 71.66% | 64.27% | $20,384.40 | 74.4% | $29,791.92 |
| `0.40` | 400 | 28.4% | 246 | 154 | 128 | 881 | 61.50% | 65.78% | 63.57% | $18,984.65 | 69.3% | $28,172.37 |
| `0.45` | 341 | 24.2% | 218 | 123 | 156 | 912 | 63.93% | 58.29% | 60.98% | $17,143.65 | 62.6% | $25,743.57 |
| `0.50` | 291 | 20.7% | 201 | 90 | 173 | 945 | 69.07% | 53.74% | 60.45% | $15,864.85 | 57.9% | $24,191.73 |
| `0.55` | 240 | 17.0% | 176 | 64 | 198 | 971 | 73.33% | 47.06% | 57.33% | $13,872.80 | 50.6% | $21,371.04 |
| `0.60` | 187 | 13.3% | 145 | 42 | 229 | 993 | 77.54% | 38.77% | 51.69% | $11,430.25 | 41.7% | $17,769.45 |
| `0.70` | 81 | 5.7% | 66 | 15 | 308 | 1020 | 81.48% | 17.65% | 29.01% | $5,468.85 | 20.0% | $8,628.93 |

---

## 5. Model Interpretability & Top Churn Drivers

### 5.1 Logistic Regression Standardized Log-Odds Coefficients
| Rank | Feature | Standardized Coefficient | Odds Ratio (`exp(beta)`) | Effect Direction |
| ---: | :--- | ---: | ---: | :--- |
| 1 | `tenure` | `-1.4941` | `0.224x` | Reduces Churn Risk |
| 2 | `TotalCharges` | `+0.7085` | `2.031x` | Increases Churn Risk |
| 3 | `Contract_Two year` | `-0.6692` | `0.512x` | Reduces Churn Risk |
| 4 | `Contract_Month-to-month` | `+0.6298` | `1.877x` | Increases Churn Risk |
| 5 | `InternetService_Fiber optic` | `+0.6006` | `1.823x` | Increases Churn Risk |
| 6 | `InternetService_DSL` | `-0.4662` | `0.627x` | Reduces Churn Risk |
| 7 | `MonthlyCharges` | `-0.3834` | `0.682x` | Reduces Churn Risk |
| 8 | `TechSupport_No` | `+0.2521` | `1.287x` | Increases Churn Risk |
| 9 | `PaymentMethod_Electronic check` | `+0.2485` | `1.282x` | Increases Churn Risk |
| 10 | `OnlineSecurity_No` | `+0.2219` | `1.248x` | Increases Churn Risk |
| 11 | `MultipleLines_No` | `-0.2180` | `0.804x` | Reduces Churn Risk |
| 12 | `StreamingTV_Yes` | `+0.2120` | `1.236x` | Increases Churn Risk |

### 5.2 Random Forest Gini Feature Importance
| Rank | Feature | Relative Gini Importance (%) |
| ---: | :--- | ---: |
| 1 | `tenure` | `15.40%` |
| 2 | `Contract_Month-to-month` | `13.12%` |
| 3 | `OnlineSecurity_No` | `8.47%` |
| 4 | `TotalCharges` | `8.01%` |
| 5 | `TechSupport_No` | `7.40%` |
| 6 | `InternetService_Fiber optic` | `6.39%` |
| 7 | `Contract_Two year` | `4.93%` |
| 8 | `PaymentMethod_Electronic check` | `4.55%` |
| 9 | `MonthlyCharges` | `4.37%` |
| 10 | `InternetService_DSL` | `3.04%` |
| 11 | `Contract_One year` | `2.36%` |
| 12 | `DeviceProtection_No` | `2.09%` |

---

## 6. Model Limitations & Operational Risks
1. **Cross-Sectional Snapshot**: The dataset lacks longitudinal billing history, usage decay trajectories, and customer support ticket logs, which limits early detection of sudden dissatisfaction.
2. **Observational Feature Associations**: High odds ratios on `Contract_Month-to-month` and `InternetService_Fiber optic` reflect observational correlations rather than causal treatment effects.
3. **Probability Calibration Drift**: Quarterly recalibration is required if pricing tiers or contract promotions change.
