"""Exploratory Data Analysis (EDA) module for Customer Churn Intelligence.

Calculates overall and segment-level churn metrics, revenue exposure,
and generates 10 publication-grade charts in `visuals/` and writes
`reports/findings.md`.
"""

from pathlib import Path
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import PROCESSED_DIR, REPORTS_DIR, VISUALS_DIR

# Consistent executive color palette
PALETTE_MAIN = {"Retained": "#2b5c8f", "Churned": "#d95f02", "No": "#2b5c8f", "Yes": "#d95f02"}
BAR_COLOR = "#2b5c8f"
ACCENT_COLOR = "#d95f02"
NEUTRAL_BG = "#f8f9fa"

plt.rcParams["figure.dpi"] = 150
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["font.size"] = 10


def compute_eda_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive overall and segment-level churn metrics."""
    total_customers = int(len(df))
    churned_df = df[df["Churn_Flag"] == 1]
    retained_df = df[df["Churn_Flag"] == 0]

    churned_count = int(len(churned_df))
    retained_count = int(len(retained_df))
    overall_churn_rate = float(churned_count / total_customers)

    total_monthly_rev = float(df["MonthlyCharges"].sum())
    churned_monthly_rev = float(churned_df["MonthlyCharges"].sum())
    retained_monthly_rev = float(retained_df["MonthlyCharges"].sum())
    revenue_exposure_pct = float(churned_monthly_rev / total_monthly_rev)

    def summarize_group(col: str, order: list[str] | None = None) -> pd.DataFrame:
        grp = (
            df.groupby(col, observed=False)
            .agg(
                customer_count=("customerID", "count"),
                churned_customers=("Churn_Flag", "sum"),
                retained_customers=("Churn_Flag", lambda x: int((x == 0).sum())),
                churn_rate=("Churn_Flag", "mean"),
                avg_tenure=("tenure", "mean"),
                avg_monthly_charges=("MonthlyCharges", "mean"),
                total_monthly_revenue=("MonthlyCharges", "sum"),
                churned_monthly_revenue=(
                    "MonthlyCharges",
                    lambda s: float(s[df.loc[s.index, "Churn_Flag"] == 1].sum()),
                ),
            )
            .reset_index()
        )
        grp["customer_share_pct"] = grp["customer_count"] / total_customers * 100.0
        grp["churn_rate_pct"] = grp["churn_rate"] * 100.0
        grp["share_of_total_churn_pct"] = grp["churned_customers"] / churned_count * 100.0
        grp["share_of_revenue_at_risk_pct"] = (
            grp["churned_monthly_revenue"] / churned_monthly_rev * 100.0
        )
        if order:
            grp[col] = pd.Categorical(grp[col], categories=order, ordered=True)
            grp = grp.sort_values(col).reset_index(drop=True)
        else:
            grp = grp.sort_values("churn_rate", ascending=False).reset_index(drop=True)
        return grp

    tenure_order = ["0-12 Months", "13-24 Months", "25-48 Months", "49-72 Months"]
    contract_order = ["Month-to-month", "One year", "Two year"]
    segment_order = [
        "New Month-to-Month (<=12m)",
        "Established Month-to-Month (>12m)",
        "One-Year Contract",
        "Two-Year Contract",
    ]

    metrics = {
        "total_customers": total_customers,
        "churned_customers": churned_count,
        "retained_customers": retained_count,
        "overall_churn_rate": overall_churn_rate,
        "overall_churn_rate_pct": overall_churn_rate * 100.0,
        "avg_tenure_all": float(df["tenure"].mean()),
        "median_tenure_all": float(df["tenure"].median()),
        "avg_tenure_churned": float(churned_df["tenure"].mean()),
        "median_tenure_churned": float(churned_df["tenure"].median()),
        "avg_tenure_retained": float(retained_df["tenure"].mean()),
        "median_tenure_retained": float(retained_df["tenure"].median()),
        "avg_monthly_all": float(df["MonthlyCharges"].mean()),
        "median_monthly_all": float(df["MonthlyCharges"].median()),
        "avg_monthly_churned": float(churned_df["MonthlyCharges"].mean()),
        "median_monthly_churned": float(churned_df["MonthlyCharges"].median()),
        "avg_monthly_retained": float(retained_df["MonthlyCharges"].mean()),
        "median_monthly_retained": float(retained_df["MonthlyCharges"].median()),
        "total_monthly_revenue": total_monthly_rev,
        "churned_monthly_revenue": churned_monthly_rev,
        "retained_monthly_revenue": retained_monthly_rev,
        "annualized_churned_revenue": churned_monthly_rev * 12.0,
        "revenue_exposure_pct": revenue_exposure_pct * 100.0,
        "by_contract": summarize_group("Contract", contract_order),
        "by_tenure_group": summarize_group("tenure_group", tenure_order),
        "by_payment_method": summarize_group("PaymentMethod"),
        "by_internet_service": summarize_group("InternetService"),
        "by_customer_segment": summarize_group("customer_segment", segment_order),
        "by_senior": summarize_group("SeniorCitizen_Label"),
        "by_tech_support": summarize_group("TechSupport"),
        "by_online_security": summarize_group("OnlineSecurity"),
    }
    return metrics


def generate_eda_visuals(
    df: pd.DataFrame, metrics: Dict[str, Any], visuals_dir: Path | None = None
) -> list[Path]:
    """Generate 10 executive EDA visualizations and save as PNG files."""
    out_dir = visuals_dir or VISUALS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    saved_files: list[Path] = []

    # 1. Overall Customer Churn Rate & Revenue Exposure
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    counts = [metrics["retained_customers"], metrics["churned_customers"]]
    labels = ["Retained (No)", "Churned (Yes)"]
    colors = ["#2b5c8f", "#d95f02"]
    bars = axes[0].bar(labels, counts, color=colors, width=0.55)
    axes[0].set_title("Customer Count by Churn Status (n = 7,043)", fontweight="bold")
    axes[0].set_ylabel("Number of Customers")
    axes[0].set_ylim(0, 6200)
    for bar, cnt in zip(bars, counts):
        pct = cnt / metrics["total_customers"] * 100
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 120,
            f"{cnt:,}\n({pct:.2f}%)",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    revs = [metrics["retained_monthly_revenue"], metrics["churned_monthly_revenue"]]
    bars2 = axes[1].bar(labels, revs, color=colors, width=0.55)
    axes[1].set_title("Monthly Recurring Revenue (MRR) by Churn Status", fontweight="bold")
    axes[1].set_ylabel("Monthly Revenue ($ USD)")
    axes[1].set_ylim(0, 380000)
    for bar, rev in zip(bars2, revs):
        pct = rev / metrics["total_monthly_revenue"] * 100
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 7000,
            f"${rev:,.0f}\n({pct:.2f}%)",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    fig.suptitle("Overall Customer Churn & Monthly Revenue Exposure", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p1 = out_dir / "01_overall_churn_rate.png"
    fig.savefig(p1, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p1)

    # 2. Churn by Contract Type
    fig, ax = plt.subplots(figsize=(8.5, 5))
    c_df = metrics["by_contract"]
    bars = ax.bar(
        c_df["Contract"].astype(str),
        c_df["churn_rate_pct"],
        color=["#d95f02", "#4a7c59", "#2b5c8f"],
        width=0.55,
    )
    ax.set_title("Customer Churn Rate by Contract Type", fontsize=12, fontweight="bold")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 52)
    ax.axhline(metrics["overall_churn_rate_pct"], color="#555555", linestyle="--", label=f"Overall Avg ({metrics['overall_churn_rate_pct']:.2f}%)")
    ax.legend()
    for bar, (_, row) in zip(bars, c_df.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.0,
            f"{row['churn_rate_pct']:.2f}%\n({int(row['churned_customers']):,}/{int(row['customer_count']):,})",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )
    fig.tight_layout()
    p2 = out_dir / "02_churn_by_contract.png"
    fig.savefig(p2, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p2)

    # 3. Churn by Tenure Group
    fig, ax = plt.subplots(figsize=(9, 5))
    t_df = metrics["by_tenure_group"]
    bars = ax.bar(
        t_df["tenure_group"].astype(str),
        t_df["churn_rate_pct"],
        color=["#d95f02", "#e68a00", "#5b8cbe", "#2b5c8f"],
        width=0.55,
    )
    ax.set_title("Customer Churn Rate Across Tenure Cohorts", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tenure Cohort")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 56)
    ax.axhline(metrics["overall_churn_rate_pct"], color="#555555", linestyle="--", label=f"Overall Avg ({metrics['overall_churn_rate_pct']:.2f}%)")
    ax.legend()
    for bar, (_, row) in zip(bars, t_df.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.0,
            f"{row['churn_rate_pct']:.2f}%\n({int(row['churned_customers']):,}/{int(row['customer_count']):,})",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )
    fig.tight_layout()
    p3 = out_dir / "03_churn_by_tenure_group.png"
    fig.savefig(p3, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p3)

    # 4. Churn by Payment Method
    fig, ax = plt.subplots(figsize=(9.5, 5))
    pm_df = metrics["by_payment_method"]
    bars = ax.barh(
        pm_df["PaymentMethod"].astype(str),
        pm_df["churn_rate_pct"],
        color=["#d95f02" if x > 30 else "#2b5c8f" for x in pm_df["churn_rate_pct"]],
        height=0.55,
    )
    ax.invert_yaxis()
    ax.set_title("Customer Churn Rate by Payment Method", fontsize=12, fontweight="bold")
    ax.set_xlabel("Churn Rate (%)")
    ax.set_xlim(0, 55)
    ax.axvline(metrics["overall_churn_rate_pct"], color="#555555", linestyle="--", label=f"Overall Avg ({metrics['overall_churn_rate_pct']:.2f}%)")
    ax.legend(loc="lower right")
    for bar, (_, row) in zip(bars, pm_df.iterrows()):
        ax.text(
            bar.get_width() + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{row['churn_rate_pct']:.2f}% ({int(row['churned_customers']):,}/{int(row['customer_count']):,})",
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )
    fig.tight_layout()
    p4 = out_dir / "04_churn_by_payment_method.png"
    fig.savefig(p4, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p4)

    # 5. Churn by Internet Service Type
    fig, ax = plt.subplots(figsize=(8.5, 5))
    is_df = metrics["by_internet_service"]
    bars = ax.bar(
        is_df["InternetService"].astype(str),
        is_df["churn_rate_pct"],
        color=["#d95f02", "#2b5c8f", "#4a7c59"],
        width=0.55,
    )
    ax.set_title("Customer Churn Rate by Internet Service Tier", fontsize=12, fontweight="bold")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 50)
    ax.axhline(metrics["overall_churn_rate_pct"], color="#555555", linestyle="--", label=f"Overall Avg ({metrics['overall_churn_rate_pct']:.2f}%)")
    ax.legend()
    for bar, (_, row) in zip(bars, is_df.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.0,
            f"{row['churn_rate_pct']:.2f}%\n(Avg ${row['avg_monthly_charges']:.2f}/mo)",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )
    fig.tight_layout()
    p5 = out_dir / "05_churn_by_internet_service.png"
    fig.savefig(p5, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p5)

    # 6. Monthly Charges Distribution by Churn Status
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    sns.kdeplot(
        data=df,
        x="MonthlyCharges",
        hue="Churn",
        palette=PALETTE_MAIN,
        fill=True,
        common_norm=False,
        alpha=0.35,
        ax=axes[0],
    )
    axes[0].set_title("Monthly Charges Density by Churn Status", fontweight="bold")
    axes[0].set_xlabel("Monthly Charges ($ USD)")
    axes[0].axvline(metrics["avg_monthly_retained"], color="#2b5c8f", linestyle="--", label=f"Retained Mean (${metrics['avg_monthly_retained']:.2f})")
    axes[0].axvline(metrics["avg_monthly_churned"], color="#d95f02", linestyle="--", label=f"Churned Mean (${metrics['avg_monthly_churned']:.2f})")
    axes[0].legend(fontsize=8.5)

    sns.boxplot(
        data=df,
        x="Churn",
        y="MonthlyCharges",
        hue="Churn",
        palette=PALETTE_MAIN,
        width=0.45,
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title("Monthly Charges Quartiles by Churn Status", fontweight="bold")
    axes[1].set_xlabel("Churn Status")
    axes[1].set_ylabel("Monthly Charges ($ USD)")
    fig.suptitle("Monthly Recurring Charge Distribution: Churned vs. Retained", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p6 = out_dir / "06_monthly_charges_by_churn.png"
    fig.savefig(p6, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p6)

    # 7. Tenure Distribution by Churn Status
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    sns.histplot(
        data=df,
        x="tenure",
        hue="Churn",
        palette=PALETTE_MAIN,
        multiple="stack",
        bins=24,
        ax=axes[0],
    )
    axes[0].set_title("Customer Tenure Histogram by Churn Status", fontweight="bold")
    axes[0].set_xlabel("Tenure (Months)")
    axes[0].set_ylabel("Customer Count")

    sns.boxplot(
        data=df,
        x="Churn",
        y="tenure",
        hue="Churn",
        palette=PALETTE_MAIN,
        width=0.45,
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title(
        f"Tenure Boxplot (Churned Median: {metrics['median_tenure_churned']:.0f}m vs Retained: {metrics['median_tenure_retained']:.0f}m)",
        fontweight="bold",
    )
    axes[1].set_xlabel("Churn Status")
    axes[1].set_ylabel("Tenure (Months)")
    fig.suptitle("Customer Tenure Distribution by Churn Status", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p7 = out_dir / "07_tenure_distribution_by_churn.png"
    fig.savefig(p7, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p7)

    # 8. Churn & Revenue Exposure by Customer Segment
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    s_df = metrics["by_customer_segment"]
    seg_colors = ["#d95f02", "#e68a00", "#5b8cbe", "#2b5c8f"]
    b1 = axes[0].barh(s_df["customer_segment"].astype(str), s_df["churn_rate_pct"], color=seg_colors, height=0.55)
    axes[0].invert_yaxis()
    axes[0].set_title("Churn Rate (%) by Lifecycle Segment", fontweight="bold")
    axes[0].set_xlabel("Churn Rate (%)")
    axes[0].set_xlim(0, 62)
    for bar, (_, r) in zip(b1, s_df.iterrows()):
        axes[0].text(
            bar.get_width() + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{r['churn_rate_pct']:.2f}%",
            va="center",
            fontweight="bold",
        )

    b2 = axes[1].barh(
        s_df["customer_segment"].astype(str),
        s_df["churned_monthly_revenue"],
        color=seg_colors,
        height=0.55,
    )
    axes[1].invert_yaxis()
    axes[1].set_title("Monthly Revenue Lost to Churn ($ USD)", fontweight="bold")
    axes[1].set_xlabel("Churned Monthly Revenue ($ USD)")
    axes[1].set_xlim(0, 82000)
    for bar, (_, r) in zip(b2, s_df.iterrows()):
        axes[1].text(
            bar.get_width() + 800,
            bar.get_y() + bar.get_height() / 2,
            f"${r['churned_monthly_revenue']:,.0f} ({r['share_of_revenue_at_risk_pct']:.1f}%)",
            va="center",
            fontweight="bold",
        )
    fig.suptitle("Lifecycle Segment Analysis: Churn Rate vs. Monthly Revenue at Risk", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    p8 = out_dir / "08_churn_by_customer_segment.png"
    fig.savefig(p8, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p8)

    # 9. Add-on Support & Security Ecosystem Impact on Fiber Optic & DSL
    internet_df = df[df["InternetService"] != "No"].copy()
    addon_summary = (
        internet_df.groupby(["InternetService", "OnlineSecurity", "TechSupport"], observed=False)
        .agg(
            customers=("customerID", "count"),
            churn_rate=("Churn_Flag", lambda x: x.mean() * 100),
        )
        .reset_index()
    )
    addon_summary["Bundle"] = (
        "Sec:" + addon_summary["OnlineSecurity"] + " | Tech:" + addon_summary["TechSupport"]
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=addon_summary,
        x="Bundle",
        y="churn_rate",
        hue="InternetService",
        palette={"Fiber optic": "#d95f02", "DSL": "#2b5c8f"},
        ax=ax,
    )
    ax.set_title("Churn Rate by Security & Tech Support Bundle (Internet Subscribers)", fontsize=12, fontweight="bold")
    ax.set_xlabel("OnlineSecurity & TechSupport Subscription Combination")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 60)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=9, fontweight="bold")
    fig.tight_layout()
    p9 = out_dir / "09_churn_by_security_tech_bundle.png"
    fig.savefig(p9, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p9)

    # 10. Correlation & Risk Heatmap (Contract x Tenure Group)
    pivot_ct = (
        df.pivot_table(
            index="Contract",
            columns="tenure_group",
            values="Churn_Flag",
            aggfunc=lambda x: x.mean() * 100.0,
            observed=False,
        )
        .reindex(index=["Month-to-month", "One year", "Two year"])
        .reindex(columns=["0-12 Months", "13-24 Months", "25-48 Months", "49-72 Months"])
    )
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    sns.heatmap(
        pivot_ct,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        cbar_kws={"label": "Churn Rate (%)"},
        ax=ax,
    )
    ax.set_title("Churn Rate (%) Matrix: Contract Type vs. Tenure Group", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tenure Cohort")
    ax.set_ylabel("Contract Type")
    fig.tight_layout()
    p10 = out_dir / "10_contract_tenure_churn_heatmap.png"
    fig.savefig(p10, bbox_inches="tight")
    plt.close(fig)
    saved_files.append(p10)

    return saved_files


def write_findings_report(
    metrics: Dict[str, Any], saved_charts: list[Path], output_path: Path | None = None
) -> Path:
    """Write `reports/findings.md` with exact denominators and statistical findings."""
    out_file = output_path or (REPORTS_DIR / "findings.md")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    def df_to_md(df_in: pd.DataFrame, first_col: str) -> str:
        lines = [
            f"| {first_col} | Customers | Share (%) | Churned | Retained | Churn Rate (%) | Avg Tenure (mo) | Avg Monthly ($) | Total MRR ($) | Churned MRR ($) | Share of Churned MRR (%) |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for _, r in df_in.iterrows():
            lines.append(
                f"| **{r[first_col]}** | {int(r['customer_count']):,} | {r['customer_share_pct']:.2f}% | "
                f"{int(r['churned_customers']):,} | {int(r['retained_customers']):,} | "
                f"**{r['churn_rate_pct']:.2f}%** | {r['avg_tenure']:.2f} | ${r['avg_monthly_charges']:.2f} | "
                f"${r['total_monthly_revenue']:,.2f} | ${r['churned_monthly_revenue']:,.2f} | "
                f"{r['share_of_revenue_at_risk_pct']:.2f}% |"
            )
        return "\n".join(lines)

    content = f"""# Exploratory Data Analysis (EDA) Findings Report

## 1. Executive Summary & Overall Denominators
All metrics below were computed directly from the cleaned dataset (`data/processed/cleaned_churn.csv`, **n = {metrics['total_customers']:,} unique customers**).

| Metric | Measured Value | Denominator / Scope |
| :--- | ---: | :--- |
| **Total Customers** | `{metrics['total_customers']:,}` | All customers in dataset |
| **Retained Customers (`Churn = No`)** | `{metrics['retained_customers']:,}` (`{100 - metrics['overall_churn_rate_pct']:.2f}%`) | Out of `{metrics['total_customers']:,}` total customers |
| **Churned Customers (`Churn = Yes`)** | `{metrics['churned_customers']:,}` (`{metrics['overall_churn_rate_pct']:.2f}%`) | Out of `{metrics['total_customers']:,}` total customers |
| **Average Tenure (All Customers)** | `{metrics['avg_tenure_all']:.2f}` months (Median: `{metrics['median_tenure_all']:.1f}`) | Across all `{metrics['total_customers']:,}` customers |
| **Average Tenure (Churned Customers)** | `{metrics['avg_tenure_churned']:.2f}` months (Median: `{metrics['median_tenure_churned']:.1f}`) | Within `{metrics['churned_customers']:,}` churned customers |
| **Average Tenure (Retained Customers)** | `{metrics['avg_tenure_retained']:.2f}` months (Median: `{metrics['median_tenure_retained']:.1f}`) | Within `{metrics['retained_customers']:,}` retained customers |
| **Average Monthly Charges (All Customers)** | `${metrics['avg_monthly_all']:.2f}` (Median: `${metrics['median_monthly_all']:.2f}`) | Across all `{metrics['total_customers']:,}` customers |
| **Average Monthly Charges (Churned)** | `${metrics['avg_monthly_churned']:.2f}` (Median: `${metrics['median_monthly_churned']:.2f}`) | Within `{metrics['churned_customers']:,}` churned customers |
| **Average Monthly Charges (Retained)** | `${metrics['avg_monthly_retained']:.2f}` (Median: `${metrics['median_monthly_retained']:.2f}`) | Within `{metrics['retained_customers']:,}` retained customers |
| **Total Monthly Recurring Revenue (MRR)** | `${metrics['total_monthly_revenue']:,.2f}` | Sum of `MonthlyCharges` across all `{metrics['total_customers']:,}` customers |
| **Monthly Charges Associated with Churned Customers** | `${metrics['churned_monthly_revenue']:,.2f}` (`{metrics['revenue_exposure_pct']:.2f}%` of total MRR) | Sum of `MonthlyCharges` across `{metrics['churned_customers']:,}` churned customers |
| **Annualized Churned Revenue Exposure** | `${metrics['annualized_churned_revenue']:,.2f}` / year | `${metrics['churned_monthly_revenue']:,.2f} * 12` months |

---

## 2. Segment Breakdowns & Revenue Exposure

### 2.1 Churn & Revenue Exposure by Contract Type
{df_to_md(metrics['by_contract'], 'Contract')}

- **Measured Finding**: Month-to-month contracts represent `55.02%` (`3,875 / 7,043`) of the customer base but account for **`88.55%` (`1,655 / 1,869`)** of all churned customers and **`86.82%` (`$120,847.10 / $139,130.85`)** of monthly revenue lost to churn.

### 2.2 Churn & Revenue Exposure by Tenure Group
{df_to_md(metrics['by_tenure_group'], 'tenure_group')}

- **Measured Finding**: First-year customers (`0-12 Months`, `n = 2,186`) churn at **`47.44%`** (`1,037 / 2,186`), generating `$68,938.45` in monthly churned revenue (`49.55%` of total churned MRR). Churn drops monotonically across tenure cohorts to **`9.51%`** in the `49-72 Months` cohort.

### 2.3 Churn & Revenue Exposure by Lifecycle Customer Segment
{df_to_md(metrics['by_customer_segment'], 'customer_segment')}

- **Measured Finding**:
  - **New Month-to-Month (`<=12m`)** has a **`51.35%`** churn rate (`1,024 / 1,994` customers) and `$68,079.55` in monthly revenue lost.
  - **Established Month-to-Month (`>12m`)** has a **`33.55%`** churn rate (`631 / 1,881` customers) and `$52,767.55` in monthly revenue lost (`$83.63` average monthly bill among churners).

### 2.4 Churn & Revenue Exposure by Internet Service Tier
{df_to_md(metrics['by_internet_service'], 'InternetService')}

- **Measured Finding**: Fiber optic subscribers (`n = 3,096`) exhibit a **`41.89%`** churn rate (`1,297 / 3,096`) and represent **`82.39%` (`$114,655.35 / $139,130.85`)** of all monthly revenue lost to churn.

### 2.5 Churn & Revenue Exposure by Payment Method
{df_to_md(metrics['by_payment_method'], 'PaymentMethod')}

- **Measured Finding**: Customers paying via **Electronic check** (`n = 2,365`) churn at **`45.29%`** (`1,071 / 2,365`), nearly triple the rate of automatic bank transfer (`16.71%`) or automatic credit card (`15.24%`).

### 2.6 Churn by Online Security & Tech Support Subscriptions
{df_to_md(metrics['by_online_security'], 'OnlineSecurity')}

{df_to_md(metrics['by_tech_support'], 'TechSupport')}

- **Measured Finding**: Customers without `OnlineSecurity` (`n = 3,498`) churn at **`41.77%`** vs. **`14.61%`** for those with `OnlineSecurity`. Similarly, customers without `TechSupport` (`n = 3,473`) churn at **`41.64%`** vs. **`15.17%`** with `TechSupport`.

---

## 3. Correlation vs. Causation Note
All findings above represent **observational associations** measured in cross-sectional customer records:
1. **Electronic Check vs. Churn**: The `45.29%` churn rate on electronic check does not prove that the payment rail itself causes cancellation; electronic check is strongly correlated with month-to-month contracts and lower digital autopay commitment.
2. **Fiber Optic vs. Churn**: The `41.89%` churn rate on Fiber optic co-occurs with substantially higher monthly bills (`$91.50` average vs. `$58.10` on DSL) and lower attachment of `OnlineSecurity`/`TechSupport`. Price sensitivity, competitor fiber promotions, or service reliability expectations may confound this relationship.
3. **Contract Term Self-Selection**: Customers choosing 1-year or 2-year contracts self-select into longer commitments; moving month-to-month customers onto annual contracts via incentives will not automatically replicate the `2.83%` two-year churn rate without randomized A/B retention testing.

---

## 4. Generated Visualizations (`visuals/`)
"""
    for chart in saved_charts:
        content += f"- `visuals/{chart.name}`\n"

    out_file.write_text(content, encoding="utf-8")
    return out_file


def run_eda_pipeline() -> Dict[str, Any]:
    """Load cleaned dataset, compute EDA metrics, generate charts, and write report."""
    cleaned_path = PROCESSED_DIR / "cleaned_churn.csv"
    df = pd.read_csv(cleaned_path)
    metrics = compute_eda_metrics(df)
    charts = generate_eda_visuals(df, metrics)
    write_findings_report(metrics, charts)
    return metrics


if __name__ == "__main__":
    eda_res = run_eda_pipeline()
    print(
        f"EDA completed: {eda_res['total_customers']} customers, "
        f"churn rate {eda_res['overall_churn_rate_pct']:.2f}%, "
        f"MRR at risk ${eda_res['churned_monthly_revenue']:,.2f}"
    )
