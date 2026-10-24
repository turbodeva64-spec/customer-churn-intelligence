import unittest
import json
import pandas as pd
from src.config import PROCESSED_DIR, MODELS_DIR
from src.database import DatabaseManager

class TestMetricsReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(PROCESSED_DIR / "cleaned_churn.csv")
        cls.db = DatabaseManager()
        with open(MODELS_DIR / "training_metrics.json", "r", encoding="utf-8") as f:
            cls.ml_metrics = json.load(f)

    def test_sql_vs_python_headline_kpis(self):
        sql_kpis = self.db.execute_query("""
            SELECT 
                COUNT(*) AS total_customers,
                SUM(Churn_Flag) AS churned_customers,
                ROUND(AVG(Churn_Flag) * 100.0, 2) AS churn_rate_pct,
                ROUND(SUM(MonthlyCharges), 2) AS total_mrr,
                ROUND(SUM(CASE WHEN Churn_Flag = 1 THEN MonthlyCharges ELSE 0 END), 2) AS churned_mrr
            FROM customer_churn;
        """).iloc[0]

        py_total = len(self.df)
        py_churned = int(self.df["Churn_Flag"].sum())
        py_rate = round(self.df["Churn_Flag"].mean() * 100.0, 2)
        py_mrr = round(float(self.df["MonthlyCharges"].sum()), 2)
        py_churned_mrr = round(float(self.df.loc[self.df["Churn_Flag"] == 1, "MonthlyCharges"].sum()), 2)

        self.assertEqual(int(sql_kpis["total_customers"]), py_total)
        self.assertEqual(int(sql_kpis["churned_customers"]), py_churned)
        self.assertAlmostEqual(float(sql_kpis["churn_rate_pct"]), py_rate, places=2)
        self.assertAlmostEqual(float(sql_kpis["total_mrr"]), py_mrr, places=2)
        self.assertAlmostEqual(float(sql_kpis["churned_mrr"]), py_churned_mrr, places=2)

    def test_contract_churn_reconciliation(self):
        sql_contract = self.db.execute_query("""
            SELECT Contract, COUNT(*) AS n, SUM(Churn_Flag) AS churned
            FROM customer_churn GROUP BY Contract;
        """).set_index("Contract")

        py_contract = self.df.groupby("Contract")["Churn_Flag"].agg(n="count", churned="sum")
        for contract in ["Month-to-month", "One year", "Two year"]:
            self.assertEqual(int(sql_contract.loc[contract, "n"]), int(py_contract.loc[contract, "n"]))
            self.assertEqual(int(sql_contract.loc[contract, "churned"]), int(py_contract.loc[contract, "churned"]))

    def test_ml_metrics_bounds(self):
        for model_name in ["Logistic Regression", "Random Forest"]:
            test_m = self.ml_metrics["test_metrics_050"][model_name]
            self.assertGreater(test_m["roc_auc"], 0.80)
            self.assertGreater(test_m["pr_auc"], 0.60)
            self.assertEqual(test_m["tn"] + test_m["fp"] + test_m["fn"] + test_m["tp"], 1409)

if __name__ == "__main__":
    unittest.main()
