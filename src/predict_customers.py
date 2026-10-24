"""Customer-level churn probability scoring and retention prioritization module.

Loads the saved champion pipeline (`models/churn_model_pipeline.pkl`), scores
all customer records, assigns actionable risk tiers and recommended retention
interventions, and exports `data/predictions/customer_risk_predictions.csv`.
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import MODELS_DIR, PREDICTIONS_DIR, PROCESSED_DIR
from src.train_model import run_training_pipeline


def assign_risk_tier(prob: pd.Series) -> pd.Series:
    """Assign customer churn risk tier from predicted probability."""
    conditions = [
        prob >= 0.60,
        (prob >= 0.35) & (prob < 0.60),
        prob < 0.35,
    ]
    choices = [
        "High Risk",
        "Medium Risk",
        "Low Risk",
    ]
    return pd.Series(np.select(conditions, choices, default="Low Risk"), index=prob.index)


def assign_recommended_action(df: pd.DataFrame) -> pd.Series:
    """Assign targeted retention action based on risk tier and service profile."""
    conditions = [
        (df["risk_tier"] == "High Risk")
        & (df["Contract"] == "Month-to-month")
        & (df["InternetService"] == "Fiber optic"),
        (df["risk_tier"] == "High Risk") & (df["Contract"] == "Month-to-month"),
        df["risk_tier"] == "High Risk",
        (df["risk_tier"] == "Medium Risk") & (df["is_auto_pay"] == 0),
        df["risk_tier"] == "Medium Risk",
    ]
    choices = [
        "Priority Outreach: 1-Yr Contract Upgrade + Free TechSupport/Security Bundle",
        "Onboarding/Contract Offer: Annual Plan Discount + Auto-Pay Enrollment",
        "Account Executive Review: Service Quality & Loyalty Check-In",
        "Digital Nudge: $5/mo Auto-Pay & Paperless Billing Incentive",
        "Proactive Engagement: Value-Add Service Bundle Offer",
    ]
    return pd.Series(
        np.select(conditions, choices, default="Standard Loyalty Monitoring"),
        index=df.index,
    )


def generate_customer_predictions(
    cleaned_df: pd.DataFrame | None = None,
    model_path: Path | None = None,
    output_path: Path | None = None,
) -> pd.DataFrame:
    """Score customers and export actionable prediction table."""
    if cleaned_df is None:
        cleaned_df = pd.read_csv(PROCESSED_DIR / "cleaned_churn.csv")

    pkl_path = model_path or (MODELS_DIR / "churn_model_pipeline.pkl")
    if not pkl_path.exists():
        run_training_pipeline(cleaned_df)

    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)

    champion = bundle["champion"]
    rf_pipe = bundle["random_forest"]

    probs = champion.predict_proba(cleaned_df)[:, 1]
    rf_probs = rf_pipe.predict_proba(cleaned_df)[:, 1]
    preds_050 = (probs >= 0.50).astype(int)
    preds_opt = (probs >= champion.optimal_threshold).astype(int)

    out_df = cleaned_df[
        [
            "customerID",
            "gender",
            "SeniorCitizen_Label",
            "Partner",
            "Dependents",
            "tenure",
            "tenure_group",
            "Contract",
            "InternetService",
            "OnlineSecurity",
            "TechSupport",
            "PaymentMethod",
            "PaperlessBilling",
            "addon_service_count",
            "is_auto_pay",
            "customer_segment",
            "MonthlyCharges",
            "TotalCharges",
            "Churn",
            "Churn_Flag",
        ]
    ].copy()

    out_df["churn_probability"] = np.round(probs, 4)
    out_df["rf_churn_probability"] = np.round(rf_probs, 4)
    out_df["predicted_churn_default_050"] = preds_050
    out_df["predicted_churn_optimal_035"] = preds_opt
    out_df["risk_tier"] = assign_risk_tier(out_df["churn_probability"])
    out_df["expected_monthly_revenue_at_risk"] = np.round(
        out_df["MonthlyCharges"] * out_df["churn_probability"], 2
    )
    out_df["expected_annual_revenue_at_risk"] = np.round(
        out_df["expected_monthly_revenue_at_risk"] * 12.0, 2
    )
    out_df["recommended_action"] = assign_recommended_action(out_df)

    out_df = out_df.sort_values(
        ["expected_monthly_revenue_at_risk", "churn_probability"], ascending=False
    ).reset_index(drop=True)
    out_df["priority_rank"] = np.arange(1, len(out_df) + 1)

    dest = output_path or (PREDICTIONS_DIR / "customer_risk_predictions.csv")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(dest, index=False)
    return out_df


if __name__ == "__main__":
    pred_df = generate_customer_predictions()
    tier_counts = pred_df["risk_tier"].value_counts().to_dict()
    print(f"Exported {len(pred_df)} customer predictions. Risk tiers: {tier_counts}")
