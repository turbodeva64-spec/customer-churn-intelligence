import unittest
import pandas as pd
from src.config import PREDICTIONS_DIR, MODELS_DIR, PROCESSED_DIR
from src.train_model import NUMERIC_FEATURES, CATEGORICAL_FEATURES

class TestPredictionsAndLeakage(unittest.TestCase):
    def test_model_artifact_and_predictions_exist(self):
        model_pkl = MODELS_DIR / "churn_model_pipeline.pkl"
        pred_csv = PREDICTIONS_DIR / "customer_risk_predictions.csv"
        self.assertTrue(model_pkl.exists())
        self.assertTrue(pred_csv.exists())
        pred_df = pd.read_csv(pred_csv)
        self.assertEqual(len(pred_df), 7043)

    def test_probability_bounds_and_risk_tiers(self):
        pred_df = pd.read_csv(PREDICTIONS_DIR / "customer_risk_predictions.csv")
        self.assertTrue((pred_df["churn_probability"] >= 0.0).all())
        self.assertTrue((pred_df["churn_probability"] <= 1.0).all())
        self.assertEqual(set(pred_df["risk_tier"].unique()), {"Low Risk", "Medium Risk", "High Risk"})
        self.assertEqual(pred_df["churn_probability"].isna().sum(), 0)

    def test_no_target_or_id_leakage_in_features(self):
        all_features = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES)
        for forbidden in ["customerID", "Churn", "Churn_Flag", "TotalCharges_Imputed_Flag"]:
            self.assertNotIn(forbidden, all_features, f"Leakage column {forbidden} found in features!")

    def test_powerbi_star_schema_exports(self):
        pbi_dir = PROCESSED_DIR / "powerbi"
        for fname in [
            "Fact_Customer_Churn.csv",
            "Dim_Customer_Profile.csv",
            "Dim_Service_Subscription.csv",
            "Dim_Billing_Contract.csv",
            "Summary_Segment_KPIs.csv",
        ]:
            fpath = pbi_dir / fname
            self.assertTrue(fpath.exists(), f"Missing Power BI export: {fname}")

if __name__ == "__main__":
    unittest.main()
