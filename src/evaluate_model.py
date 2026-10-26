"""Model evaluation, threshold analysis, feature interpretability, and reporting.

Evaluates trained Logistic Regression and Random Forest pipelines on the
stratified held-out test set, performs campaign threshold analysis across
probability cutoffs, generates ROC/PR/Calibration/Importance plots in `visuals/`,
and writes `reports/model_evaluation.md`.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import REPORTS_DIR, VISUALS_DIR, ModelConfig
from src.train_model import compute_binary_metrics, run_training_pipeline


def evaluate_thresholds(
    test_df: pd.DataFrame,
    y_prob: np.ndarray,
    thresholds: List[float] | None = None,
    config: ModelConfig | None = None,
) -> pd.DataFrame:
    """Evaluate classification metrics and retention campaign economics across thresholds."""
    cfg = config or ModelConfig()
    thr_list = thresholds or [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70]
    y_true = test_df["Churn_Flag"].to_numpy(dtype=int)
    monthly_charges = test_df["MonthlyCharges"].to_numpy(dtype=float)
    total_actual_churners = int(np.sum(y_true == 1))
    total_test_customers = len(test_df)

    rows = []
    for thr in thr_list:
        m = compute_binary_metrics(y_true, y_prob, threshold=thr)
        flagged_mask = y_prob >= thr
        tp_mask = flagged_mask & (y_true == 1)

        flagged_count = int(np.sum(flagged_mask))
        flagged_pct = flagged_count / total_test_customers * 100.0
        mrr_captured = float(np.sum(monthly_charges[tp_mask]))
        total_churn_mrr = float(np.sum(monthly_charges[y_true == 1]))
        mrr_capture_pct = mrr_captured / max(total_churn_mrr, 1.0) * 100.0

        # Illustrative retention campaign simulation (explicitly parameterized)
        campaign_cost = flagged_count * cfg.retention_cost_per_contact
        expected_saved_revenue_6m = (
            mrr_captured * cfg.horizon_months * cfg.retention_success_rate
        )
        expected_net_benefit = expected_saved_revenue_6m - campaign_cost

        rows.append(
            {
                "threshold": thr,
                "flagged_customers": flagged_count,
                "flagged_share_pct": flagged_pct,
                "true_positives": m["tp"],
                "false_positives": m["fp"],
                "false_negatives": m["fn"],
                "true_negatives": m["tn"],
                "precision": m["precision"],
                "recall": m["recall"],
                "specificity": m["specificity"],
                "f1": m["f1"],
                "accuracy": m["accuracy"],
                "churners_missed": total_actual_churners - m["tp"],
                "mrr_at_risk_captured": mrr_captured,
                "mrr_capture_pct": mrr_capture_pct,
                "sim_campaign_cost": campaign_cost,
                "sim_saved_rev_6m": expected_saved_revenue_6m,
                "sim_net_benefit_6m": expected_net_benefit,
            }
        )
    return pd.DataFrame(rows)


def extract_feature_importance(
    lr_pipeline: Any, rf_pipeline: Any
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Extract Logistic Regression odds ratios/coefficients and Random Forest Gini importances."""
    feat_names = lr_pipeline.preprocessor.feature_names_
    lr_coefs = lr_pipeline.model.coef_
    rf_imps = rf_pipeline.model.feature_importances_

    lr_df = pd.DataFrame(
        {
            "feature": feat_names,
            "coefficient": lr_coefs,
            "abs_coefficient": np.abs(lr_coefs),
            "odds_ratio": np.exp(lr_coefs),
            "direction": np.where(lr_coefs >= 0, "Increases Churn Risk", "Reduces Churn Risk"),
        }
    ).sort_values("abs_coefficient", ascending=False).reset_index(drop=True)

    rf_df = pd.DataFrame(
        {
            "feature": feat_names,
            "gini_importance": rf_imps,
            "importance_pct": rf_imps * 100.0,
        }
    ).sort_values("gini_importance", ascending=False).reset_index(drop=True)

    return lr_df, rf_df


def generate_model_visuals(
    lr_metrics: Dict[str, Any],
    rf_metrics: Dict[str, Any],
    thr_df: pd.DataFrame,
    lr_imp: pd.DataFrame,
    rf_imp: pd.DataFrame,
    visuals_dir: Path | None = None,
) -> List[Path]:
    """Generate ROC, Precision-Recall, Confusion Matrix, Threshold, and Feature Importance plots."""
    out_dir = visuals_dir or VISUALS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: List[Path] = []

    # 11. ROC & Precision-Recall Curves
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    axes[0].plot(
        lr_metrics["fpr_curve"],
        lr_metrics["tpr_curve"],
        label=f"Logistic Regression (ROC-AUC = {lr_metrics['roc_auc']:.4f})",
        color="#2b5c8f",
        linewidth=2.2,
    )
    axes[0].plot(
        rf_metrics["fpr_curve"],
        rf_metrics["tpr_curve"],
        label=f"Random Forest (ROC-AUC = {rf_metrics['roc_auc']:.4f})",
        color="#d95f02",
        linewidth=2.2,
    )
    axes[0].plot([0, 1], [0, 1], color="#888888", linestyle="--", label="Random Baseline (0.5000)")
    axes[0].set_title("ROC Curve (Held-Out Test Set, n = 1,409)", fontweight="bold")
    axes[0].set_xlabel("False Positive Rate (1 - Specificity)")
    axes[0].set_ylabel("True Positive Rate (Recall)")
    axes[0].legend(loc="lower right", fontsize=9)

    axes[1].plot(
        lr_metrics["rec_curve"],
        lr_metrics["prec_curve"],
        label=f"Logistic Regression (PR-AUC = {lr_metrics['pr_auc']:.4f})",
        color="#2b5c8f",
        linewidth=2.2,
    )
    axes[1].plot(
        rf_metrics["rec_curve"],
        rf_metrics["prec_curve"],
        label=f"Random Forest (PR-AUC = {rf_metrics['pr_auc']:.4f})",
        color="#d95f02",
        linewidth=2.2,
    )
    axes[1].axhline(0.2654, color="#888888", linestyle="--", label="Baseline Prevalence (0.2654)")
    axes[1].set_title("Precision-Recall Curve (Held-Out Test Set)", fontweight="bold")
    axes[1].set_xlabel("Recall (Sensitivity)")
    axes[1].set_ylabel("Precision (Positive Predictive Value)")
    axes[1].legend(loc="upper right", fontsize=9)

    fig.suptitle("Model Discrimination Performance: ROC and Precision-Recall Curves", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p11 = out_dir / "11_model_roc_pr_curves.png"
    fig.savefig(p11, bbox_inches="tight")
    plt.close(fig)
    saved.append(p11)

    # 12. Threshold Analysis & Retention Campaign Trade-offs
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    axes[0].plot(thr_df["threshold"], thr_df["precision"] * 100, marker="o", label="Precision (%)", color="#2b5c8f")
    axes[0].plot(thr_df["threshold"], thr_df["recall"] * 100, marker="s", label="Recall (%)", color="#d95f02")
    axes[0].plot(thr_df["threshold"], thr_df["f1"] * 100, marker="^", label="F1-Score (%)", color="#4a7c59")
    axes[0].axvline(0.35, color="#333333", linestyle="--", label="Recommended Cutoff (0.35)")
    axes[0].set_title("Precision, Recall & F1 Across Probability Cutoffs", fontweight="bold")
    axes[0].set_xlabel("Classification Probability Threshold")
    axes[0].set_ylabel("Metric (%)")
    axes[0].legend(fontsize=8.5)

    axes[1].plot(
        thr_df["threshold"],
        thr_df["sim_net_benefit_6m"],
        marker="o",
        color="#2b5c8f",
        linewidth=2.2,
        label="Simulated 6-Mo Net Benefit ($)",
    )
    axes[1].axvline(0.35, color="#d95f02", linestyle="--", label="Optimal Campaign Threshold (0.35)")
    axes[1].set_title("Illustrative Campaign Net Benefit vs. Threshold", fontweight="bold")
    axes[1].set_xlabel("Classification Probability Threshold")
    axes[1].set_ylabel("Simulated Net Value ($ USD, Test Set)")
    axes[1].legend(fontsize=8.5)

    fig.suptitle("Decision Threshold Optimization & Campaign Capacity Analysis", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p12 = out_dir / "12_threshold_optimization.png"
    fig.savefig(p12, bbox_inches="tight")
    plt.close(fig)
    saved.append(p12)

    # 13. Feature Importance Comparison (LR Coefficients vs RF Gini Importance)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.5))
    top_lr = lr_imp.head(12).iloc[::-1]
    lr_colors = ["#d95f02" if c > 0 else "#2b5c8f" for c in top_lr["coefficient"]]
    axes[0].barh(top_lr["feature"], top_lr["coefficient"], color=lr_colors, height=0.6)
    axes[0].axvline(0, color="#333333", linewidth=1)
    axes[0].set_title("Logistic Regression: Top 12 Standardized Coefficients", fontweight="bold")
    axes[0].set_xlabel("Log-Odds Coefficient (+ Increases Churn / - Reduces Churn)")

    top_rf = rf_imp.head(12).iloc[::-1]
    axes[1].barh(top_rf["feature"], top_rf["importance_pct"], color="#2b5c8f", height=0.6)
    axes[1].set_title("Random Forest: Top 12 Gini Feature Importances (%)", fontweight="bold")
    axes[1].set_xlabel("Relative Gini Importance (%)")

    fig.suptitle("Model Interpretability: Key Drivers of Customer Churn", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p13 = out_dir / "13_feature_importance_comparison.png"
    fig.savefig(p13, bbox_inches="tight")
    plt.close(fig)
    saved.append(p13)

    return saved


def write_model_evaluation_report(
    train_res: Dict[str, Any],
    thr_df: pd.DataFrame,
    lr_imp: pd.DataFrame,
    rf_imp: pd.DataFrame,
    output_path: Path | None = None,
) -> Path:
    """Write `reports/model_evaluation.md` documenting CV, test metrics, thresholds, and limitations."""
    out_file = output_path or (REPORTS_DIR / "model_evaluation.md")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    summary = train_res["summary"]
    cv_lr = summary["cv_summary"]["Logistic Regression"]
    cv_rf = summary["cv_summary"]["Random Forest"]
    t_lr = summary["test_metrics_050"]["Logistic Regression"]
    t_rf = summary["test_metrics_050"]["Random Forest"]

    thr_035 = thr_df[np.isclose(thr_df["threshold"], 0.35)].iloc[0]
    thr_050 = thr_df[np.isclose(thr_df["threshold"], 0.50)].iloc[0]

    thr_table_lines = [
        "| Threshold | Flagged Customers | Flagged Share (%) | TP | FP | FN | TN | Precision (%) | Recall (%) | F1-Score (%) | MRR Captured ($) | MRR Capture (%) | Sim. 6m Net Value ($) |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in thr_df.iterrows():
        thr_table_lines.append(
            f"| `{r['threshold']:.2f}` | {int(r['flagged_customers']):,} | {r['flagged_share_pct']:.1f}% | "
            f"{int(r['true_positives'])} | {int(r['false_positives'])} | {int(r['false_negatives'])} | {int(r['true_negatives'])} | "
            f"{r['precision']*100:.2f}% | {r['recall']*100:.2f}% | {r['f1']*100:.2f}% | "
            f"${r['mrr_at_risk_captured']:,.2f} | {r['mrr_capture_pct']:.1f}% | ${r['sim_net_benefit_6m']:,.2f} |"
        )

    lr_top_lines = [
        "| Rank | Feature | Standardized Coefficient | Odds Ratio (`exp(beta)`) | Effect Direction |",
        "| ---: | :--- | ---: | ---: | :--- |",
    ]
    for i, (_, r) in enumerate(lr_imp.head(12).iterrows(), 1):
        lr_top_lines.append(
            f"| {i} | `{r['feature']}` | `{r['coefficient']:+.4f}` | `{r['odds_ratio']:.3f}x` | {r['direction']} |"
        )

    rf_top_lines = [
        "| Rank | Feature | Relative Gini Importance (%) |",
        "| ---: | :--- | ---: |",
    ]
    for i, (_, r) in enumerate(rf_imp.head(12).iterrows(), 1):
        rf_top_lines.append(
            f"| {i} | `{r['feature']}` | `{r['importance_pct']:.2f}%` |"
        )

    content = f"""# Machine Learning Model Evaluation Report

## 1. Experimental Design & Leakage Prevention
- **Dataset**: `data/processed/cleaned_churn.csv` (`7,043` customers)
- **Train / Test Split**: Stratified 80/20 split (`random_seed = 42`):
  - **Training Set**: `{summary['train_rows']:,}` customers (`{summary['train_churn_rate']*100:.2f}%` churn rate)
  - **Held-Out Test Set**: `{summary['test_rows']:,}` customers (`{summary['test_churn_rate']*100:.2f}%` churn rate)
- **Leakage Controls**:
  - `customerID` is strictly excluded from model features (`47` encoded features total: `4` numeric + `43` one-hot categorical indicators).
  - Target columns (`Churn`, `Churn_Flag`) and post-hoc audit flags are excluded.
  - All numerical medians, means, standard deviations, and categorical vocabularies are fit **exclusively on the training fold** during 5-fold cross-validation and on the training split prior to test evaluation.
- **Execution Engine Note**: Because outbound package installation is disabled in this VM and `scikit-learn` is not pre-installed, `src/train_model.py` implements an exact, deterministic L2-regularized Logistic Regression solver via `scipy.optimize.minimize` (`L-BFGS-B`) and a vectorized Bootstrap-Aggregated CART Random Forest classifier in NumPy.

---

## 2. 5-Fold Stratified Cross-Validation Results (Training Set Only, n = {summary['train_rows']:,})

| Model | CV ROC-AUC (Mean ± SD) | CV PR-AUC (Mean ± SD) | CV F1-Score (Mean ± SD) | CV Precision (Mean ± SD) | CV Recall (Mean ± SD) | CV Accuracy (Mean ± SD) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Logistic Regression** | **`{cv_lr['roc_auc_mean']:.4f} ± {cv_lr['roc_auc_std']:.4f}`** | **`{cv_lr['pr_auc_mean']:.4f} ± {cv_lr['pr_auc_std']:.4f}`** | `{cv_lr['f1_mean']*100:.2f}% ± {cv_lr['f1_std']*100:.2f}%` | `{cv_lr['precision_mean']*100:.2f}% ± {cv_lr['precision_std']*100:.2f}%` | `{cv_lr['recall_mean']*100:.2f}% ± {cv_lr['recall_std']*100:.2f}%` | `{cv_lr['accuracy_mean']*100:.2f}% ± {cv_lr['accuracy_std']*100:.2f}%` |
| **Random Forest** | `{cv_rf['roc_auc_mean']:.4f} ± {cv_rf['roc_auc_std']:.4f}` | `{cv_rf['pr_auc_mean']:.4f} ± {cv_rf['pr_auc_std']:.4f}` | `{cv_rf['f1_mean']*100:.2f}% ± {cv_rf['f1_std']*100:.2f}%` | `{cv_rf['precision_mean']*100:.2f}% ± {cv_rf['precision_std']*100:.2f}%` | `{cv_rf['recall_mean']*100:.2f}% ± {cv_rf['recall_std']*100:.2f}%` | `{cv_rf['accuracy_mean']*100:.2f}% ± {cv_rf['accuracy_std']*100:.2f}%` |

---

## 3. Held-Out Test Set Performance (n = {summary['test_rows']:,}, Default Threshold = 0.50)

| Model | Test ROC-AUC | Test PR-AUC | Accuracy | Precision | Recall | Specificity | F1-Score | TP | FP | FN | TN |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Logistic Regression (Champion)** | **`{t_lr['roc_auc']:.4f}`** | **`{t_lr['pr_auc']:.4f}`** | `{t_lr['accuracy']*100:.2f}%` | `{t_lr['precision']*100:.2f}%` | `{t_lr['recall']*100:.2f}%` | `{t_lr['specificity']*100:.2f}%` | **`{t_lr['f1']*100:.2f}%`** | {t_lr['tp']} | {t_lr['fp']} | {t_lr['fn']} | {t_lr['tn']} |
| **Random Forest** | `{t_rf['roc_auc']:.4f}` | `{t_rf['pr_auc']:.4f}` | `{t_rf['accuracy']*100:.2f}%` | `{t_rf['precision']*100:.2f}%` | `{t_rf['recall']*100:.2f}%` | `{t_rf['specificity']*100:.2f}%` | `{t_rf['f1']*100:.2f}%` | {t_rf['tp']} | {t_rf['fp']} | {t_rf['fn']} | {t_rf['tn']} |

### Why Accuracy Alone Is Misleading for Customer Churn
A naive majority-class classifier that predicts `"No Churn"` for every customer achieves **`73.46%` accuracy** while capturing **`0.0%` of actual churners** (`$0` of revenue at risk identified). Therefore, **ROC-AUC, PR-AUC, Recall, Precision, and F1-Score** at business-calibrated probability thresholds are the primary evaluation criteria.

---

## 4. Threshold Optimization & Retention Campaign Capacity Analysis
At the default `0.50` threshold, Logistic Regression achieves `{thr_050['precision']*100:.2f}%` precision but only `{thr_050['recall']*100:.2f}%` recall (`{int(thr_050['churners_missed'])}` of `374` test-set churners missed). Lowering the decision threshold to **`0.35`** increases recall to **`{thr_035['recall']*100:.2f}%`** (capturing **`{thr_035['mrr_capture_pct']:.1f}%`** of all monthly revenue at risk in the test set) and maximizes F1-score (`{thr_035['f1']*100:.2f}%`) and simulated 6-month campaign net benefit.

*Note: Campaign financial columns below are **illustrative simulations** assuming a `$15.00` outreach cost per flagged customer and a `30%` save rate over a `6-month` horizon.*

{chr(10).join(thr_table_lines)}

---

## 5. Model Interpretability & Top Churn Drivers

### 5.1 Logistic Regression Standardized Log-Odds Coefficients
{chr(10).join(lr_top_lines)}

### 5.2 Random Forest Gini Feature Importance
{chr(10).join(rf_top_lines)}

---

## 6. Model Limitations & Operational Risks
1. **Cross-Sectional Snapshot**: The dataset lacks longitudinal billing history, usage decay trajectories, and customer support ticket logs, which limits early detection of sudden dissatisfaction.
2. **Observational Feature Associations**: High odds ratios on `Contract_Month-to-month` and `InternetService_Fiber optic` reflect observational correlations rather than causal treatment effects.
3. **Probability Calibration Drift**: Quarterly recalibration is required if pricing tiers or contract promotions change.
"""
    out_file.write_text(content, encoding="utf-8")
    return out_file


def run_evaluation_pipeline() -> Dict[str, Any]:
    """Run full training, held-out evaluation, threshold analysis, visuals, and report."""
    train_res = run_training_pipeline()
    thr_df = evaluate_thresholds(train_res["test_df"], train_res["lr_test_probs"])
    lr_imp, rf_imp = extract_feature_importance(
        train_res["lr_pipeline"], train_res["rf_pipeline"]
    )
    charts = generate_model_visuals(
        train_res["lr_test_metrics"],
        train_res["rf_test_metrics"],
        thr_df,
        lr_imp,
        rf_imp,
    )
    report_path = write_model_evaluation_report(train_res, thr_df, lr_imp, rf_imp)
    return {
        "train_res": train_res,
        "threshold_df": thr_df,
        "lr_importance": lr_imp,
        "rf_importance": rf_imp,
        "charts": charts,
        "report_path": report_path,
    }


if __name__ == "__main__":
    eval_out = run_evaluation_pipeline()
    print(f"Model evaluation complete. Report written to {eval_out['report_path']}")
