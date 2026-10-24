import unittest
import pandas as pd
from src.config import PROCESSED_DIR

class TestDataCleaning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(PROCESSED_DIR / "cleaned_churn.csv")

    def test_total_charges_imputation(self):
        # Exactly 11 rows had blank TotalCharges, all with tenure == 0
        self.assertEqual(self.df["TotalCharges"].isna().sum(), 0)
        imputed = self.df[self.df["TotalCharges_Imputed_Flag"] == 1]
        self.assertEqual(len(imputed), 11)
        self.assertTrue((imputed["tenure"] == 0).all())
        self.assertTrue((imputed["TotalCharges"] == 0.0).all())

    def test_churn_binary_encoding(self):
        self.assertEqual(set(self.df["Churn"].unique()), {"Yes", "No"})
        self.assertEqual(set(self.df["Churn_Flag"].unique()), {0, 1})
        self.assertEqual(int(self.df["Churn_Flag"].sum()), 1869)

    def test_tenure_groups_valid(self):
        expected_groups = {"0-12 Months", "13-24 Months", "25-48 Months", "49-72 Months"}
        self.assertEqual(set(self.df["tenure_group"].unique()), expected_groups)
        self.assertEqual(self.df["tenure_group"].isna().sum(), 0)

    def test_numeric_ranges(self):
        self.assertTrue((self.df["tenure"] >= 0).all() and (self.df["tenure"] <= 72).all())
        self.assertTrue((self.df["MonthlyCharges"] > 0).all())
        self.assertTrue((self.df["TotalCharges"] >= 0).all())

if __name__ == "__main__":
    unittest.main()
