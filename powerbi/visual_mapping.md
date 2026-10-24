# Power BI 4-Page Dashboard Visual Mapping Specification

## Page 1: Executive Churn Overview
- **KPI Cards (Top Ribbon)**:
  - `Total Customers` (`7,043`)
  - `Churned Customers` (`1,869`)
  - `Churn Rate` (`26.54%`)
  - `Total Monthly Recurring Revenue (MRR)` (`$456,116.60`)
  - `Monthly Revenue at Risk (Churned MRR)` (`$139,130.85`)
- **Visual 1.1 (Clustered Bar Chart)**: Churn Rate & Churned MRR by `Dim_Billing_Contract[Contract]`.
- **Visual 1.2 (Column + Line Combo Chart)**: Customer Count (Columns) and Churn Rate % (Line) by `Dim_Customer_Profile[Tenure_Group]`.
- **Visual 1.3 (Donut Chart)**: Churned MRR Share by `Dim_Service_Subscription[InternetService]`.
- **Global Slicers**: `Contract`, `InternetService`, `Tenure_Group`, `Senior_Label`.

## Page 2: Customer Risk & Revenue Exposure
- **KPI Cards**: `Predicted High-Risk Customers` (`785`), `Predicted High-Risk MRR Exposure`, `Expected Monthly Revenue Loss (Prob-Weighted)`.
- **Visual 2.1 (Matrix / Heatmap)**: `Contract` (Rows) x `InternetService` (Columns) showing `Churn Rate`, `Churned Customers`, and `Monthly Revenue at Risk (Churned MRR)`.
- **Visual 2.2 (Horizontal Bar Chart)**: Churn Rate & MRR Exposure by `Dim_Billing_Contract[PaymentMethod]`.
- **Visual 2.3 (Box / Violin Distribution)**: `Fact_Customer_Churn[MonthlyCharges]` distribution split by `Churn` status.

## Page 3: Service & Contract Drivers
- **Visual 3.1 (diverging Stacked Bar Chart)**: Churn Rate across all 6 Fiber/DSL add-on services (`OnlineSecurity`, `TechSupport`, `OnlineBackup`, `DeviceProtection`, `StreamingTV`, `StreamingMovies`).
- **Visual 3.2 (Clustered Column Chart)**: Fiber Optic Churn Rate split by `Has_Tech_Or_Security` (`0` vs `1`).
- **Visual 3.3 (Decomposition Tree)**: Root = `Churn Rate` -> `Contract` -> `InternetService` -> `Has_Tech_Or_Security` -> `Is_AutoPay`.

## Page 4: Retention Action List (Operational Workbench)
- **Slicers**: `Predicted_Risk_Tier` (default: `High Risk`), `Contract` (default: `Month-to-month`), `MonthlyCharges` slider (`>= $70`).
- **Visual 4.1 (Actionable Customer Table)**:
  - Columns: `customerID`, `Contract`, `InternetService`, `tenure`, `MonthlyCharges`, `PaymentMethod`, `Churn_Probability`, `Predicted_Risk_Tier`, `Expected_Monthly_Revenue_Loss`, `Has_Tech_Or_Security`.
  - Conditional Formatting: Red data bars on `Churn_Probability` (`>= 0.65`), amber icons on `Medium Risk` (`0.35 - 0.649`).
  - Export-ready for CRM retention campaign execution.
