import unittest
import pandas as pd
from src.config import PROCESSED_DIR, ColumnMapping
from src.database import DatabaseManager

class TestDataSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cleaned_path = PROCESSED_DIR / "cleaned_churn.csv"
        cls.dict_path = PROCESSED_DIR / "data_dictionary.csv"
        cls.col_map = ColumnMapping()
        cls.db = DatabaseManager()

    def test_cleaned_csv_exists_and_row_count(self):
        self.assertTrue(self.cleaned_path.exists(), "Cleaned CSV must exist")
        df = pd.read_csv(self.cleaned_path)
        self.assertEqual(len(df), 7043)
        for col in self.col_map.required_columns:
            self.assertIn(col, df.columns)

    def test_primary_key_uniqueness(self):
        df = pd.read_csv(self.cleaned_path)
        self.assertEqual(df["customerID"].nunique(), 7043)
        self.assertEqual(df["customerID"].isna().sum(), 0)

    def test_sqlite_tables_exist(self):
        tables = self.db.execute_query("SELECT name FROM sqlite_master WHERE type IN ('table', 'view');")
        names = set(tables["name"].tolist())
        self.assertIn("customer_churn_raw", names)
        self.assertIn("customer_churn", names)
        self.assertIn("vw_telco_cleaned", names)

    def test_data_dictionary_completeness(self):
        self.assertTrue(self.dict_path.exists())
        dd = pd.read_csv(self.dict_path)
        self.assertGreaterEqual(len(dd), 28)

if __name__ == "__main__":
    unittest.main()
