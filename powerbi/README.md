# Power BI Implementation Guide (`powerbi/`)

## Overview & Honest Scope Note
Because Microsoft Power BI Desktop (`.pbix`) is a proprietary Windows binary format that cannot be compiled headlessly on a Linux container, this folder provides the **complete, verified Power BI data model, star-schema exports, DAX measure library, and visual specifications** so you can build the `.pbix` file in under 10 minutes.

## Step-by-Step Build Instructions
1. **Load Star-Schema Tables**:
   - Open Power BI Desktop -> **Get Data** -> **Text/CSV**.
   - Load all 5 CSV files from `data/processed/powerbi/`:
     - `Fact_Customer_Churn.csv`
     - `Dim_Customer_Profile.csv`
     - `Dim_Service_Subscription.csv`
     - `Dim_Billing_Contract.csv`
     - `Summary_Segment_KPIs.csv`
2. **Configure Relationships**:
   - Follow `powerbi/relationships.md` to link `customerID` across the Fact table and the 3 Dimension tables (`1:1`, Single-direction filter from Dimension to Fact).
3. **Create DAX Measures**:
   - Create an empty `_Measures` table and paste the verified DAX formulas from `powerbi/measures.dax`.
4. **Build the 4 Dashboard Pages**:
   - Follow the exact visual-by-visual layout in `powerbi/visual_mapping.md`.
5. **Reconcile Numbers**:
   - Verify your top-level cards match the benchmark figures: Total Customers = `7,043`, Churned Customers = `1,869`, Churn Rate = `26.54%`, Total MRR = `$456,116.60`, Churned MRR = `$139,130.85`.
