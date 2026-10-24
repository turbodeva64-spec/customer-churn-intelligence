"""Power BI dataset preparation and star-schema export module.

Generates clean, Power BI-ready fact and dimension tables in `data/processed/powerbi/`
so analysts can import a ready-made star schema directly into Power BI Desktop.
"""

from pathlib import Path
from typing import Dict

import pandas as pd

from src.config import PREDICTIONS_DIR, PROCESSED_DIR


def export_powerbi_tables(output_dir: Path | None = None) -> Dict[str, Path]:
    """Create star-schema CSV tables for Power BI dashboarding."""
    pbi_dir = output_dir or (PROCESSED_DIR / "powerbi")
    pbi_dir.mkdir(parents=True, exist_ok=True)

    cleaned_df = pd.read_csv(PROCESSED_DIR / "cleaned_churn.csv")
    pred_df = pd.read_csv(PREDICTIONS_DIR / "customer_risk_predictions.csv")

    merged = cleaned_df.merge(
        pred_df[
            [
                "customerID",
                "churn_probability",
                "rf_churn_probability",
                "predicted_churn_default_050",
                "predicted_churn_optimal_035",
                "risk_tier",
                "expected_monthly_revenue_at_risk",
                "expected_annual_revenue_at_risk",
                "recommended_action",
                "priority_rank",
            ]
        ],
        on="customerID",
        how="left",
    )

    # 1. Fact_Customer_Churn
    fact_cols = [
        "customerID",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
        "TotalCharges_Imputed_Flag",
        "Churn",
        "Churn_Flag",
        "addon_service_count",
        "is_auto_pay",
        "has_family",
        "churn_probability",
        "rf_churn_probability",
        "predicted_churn_default_050",
        "predicted_churn_optimal_035",
        "risk_tier",
        "expected_monthly_revenue_at_risk",
        "expected_annual_revenue_at_risk",
        "priority_rank",
    ]
    fact_path = pbi_dir / "Fact_Customer_Churn.csv"
    merged[fact_cols].to_csv(fact_path, index=False)

    # 2. Dim_Customer_Profile
    profile_cols = [
        "customerID",
        "gender",
        "SeniorCitizen",
        "SeniorCitizen_Label",
        "Partner",
        "Dependents",
        "tenure_group",
        "customer_segment",
    ]
    dim_profile_path = pbi_dir / "Dim_Customer_Profile.csv"
    merged[profile_cols].to_csv(dim_profile_path, index=False)

    # 3. Dim_Service_Subscription
    service_cols = [
        "customerID",
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
    ]
    dim_service_path = pbi_dir / "Dim_Service_Subscription.csv"
    merged[service_cols].to_csv(dim_service_path, index=False)

    # 4. Dim_Billing_Contract
    billing_cols = [
        "customerID",
        "Contract",
        "PaperlessBilling",
        "PaymentMethod",
        "recommended_action",
    ]
    dim_billing_path = pbi_dir / "Dim_Billing_Contract.csv"
    merged[billing_cols].to_csv(dim_billing_path, index=False)

    # 5. Summary_Segment_KPIs
    seg_kpi = (
        merged.groupby(["customer_segment", "Contract", "InternetService", "risk_tier"], observed=False)
        .agg(
            customer_count=("customerID", "count"),
            churned_customers=("Churn_Flag", "sum"),
            total_mrr=("MonthlyCharges", "sum"),
            churned_mrr=(
                "MonthlyCharges",
                lambda s: float(s[merged.loc[s.index, "Churn_Flag"] == 1].sum()),
            ),
            expected_mrr_at_risk=("expected_monthly_revenue_at_risk", "sum"),
            avg_churn_prob=("churn_probability", "mean"),
        )
        .reset_index()
    )
    seg_kpi_path = pbi_dir / "Summary_Segment_KPIs.csv"
    seg_kpi.to_csv(seg_kpi_path, index=False)

    return {
        "Fact_Customer_Churn": fact_path,
        "Dim_Customer_Profile": dim_profile_path,
        "Dim_Service_Subscription": dim_service_path,
        "Dim_Billing_Contract": dim_billing_path,
        "Summary_Segment_KPIs": seg_kpi_path,
    }


if __name__ == "__main__":
    paths = export_powerbi_tables()
    for name, p in paths.items():
        print(f"Exported {name} -> {p}")
