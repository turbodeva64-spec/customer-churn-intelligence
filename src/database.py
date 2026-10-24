"""Database integration layer for Customer Churn Intelligence.

Provides read-only query execution, SQLite database initialization from the
user-provided CSV export, and schema validation without altering source files.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.config import ColumnMapping, DatabaseConfig


class DatabaseManager:
    """Manages database connections and read-only analytical queries."""

    def __init__(
        self,
        config: Optional[DatabaseConfig] = None,
        col_map: Optional[ColumnMapping] = None,
    ) -> None:
        self.config = config or DatabaseConfig()
        self.config.validate()
        self.col_map = col_map or ColumnMapping()

    def bootstrap_sqlite_from_csv(self, force: bool = False) -> Path:
        """Load the raw CSV export into a local SQLite database for native SQL execution.

        Never alters the original CSV source file. Creates both:
        1. `customer_churn_raw`: exact 1:1 representation of the raw CSV.
        2. `customer_churn`: typed analytical table with numeric TotalCharges and tenure_group.
        """
        db_path = self.config.sqlite_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)

        if db_path.exists() and not force:
            return db_path

        csv_path = self.config.raw_csv_path
        if not csv_path.exists():
            raise FileNotFoundError(f"Source CSV file not found at: {csv_path}")

        raw_df = pd.read_csv(csv_path, dtype=str)
        self.validate_required_columns(raw_df)

        # Build analytical table with exact types while preserving raw table
        typed_df = pd.read_csv(csv_path)
        typed_df["TotalCharges_raw"] = typed_df["TotalCharges"].astype(str)
        typed_df["TotalCharges"] = pd.to_numeric(
            typed_df["TotalCharges"].astype(str).str.strip().replace("", "0"),
            errors="coerce",
        ).fillna(0.0)
        typed_df["Churn_Flag"] = (typed_df["Churn"] == "Yes").astype(int)

        with sqlite3.connect(db_path) as conn:
            raw_df.to_sql("customer_churn_raw", conn, if_exists="replace", index=False)
            typed_df.to_sql(self.config.table, conn, if_exists="replace", index=False)

            # Create indexes for fast analytical querying
            conn.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{self.config.table}_cid "
                f"ON {self.config.table} (customerID);"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{self.config.table}_churn "
                f"ON {self.config.table} (Churn);"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{self.config.table}_contract "
                f"ON {self.config.table} (Contract);"
            )
        return db_path

    def get_read_only_connection(self) -> sqlite3.Connection:
        """Return a read-only SQLite connection using URI mode=ro."""
        if not self.config.sqlite_db_path.exists():
            self.bootstrap_sqlite_from_csv()
        uri = f"file:{self.config.sqlite_db_path.resolve()}?mode=ro"
        return sqlite3.connect(uri, uri=True)

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> pd.DataFrame:
        """Execute a read-only SQL query and return results as a DataFrame."""
        if self.config.db_type == "sqlite":
            with self.get_read_only_connection() as conn:
                return pd.read_sql_query(query, conn, params=params)
        raise NotImplementedError(
            f"Driver execution for {self.config.db_type} requires external DB driver."
        )

    def load_raw_dataframe(self) -> pd.DataFrame:
        """Load the untouched raw dataset from CSV or raw SQLite table."""
        if self.config.raw_csv_path.exists():
            df = pd.read_csv(self.config.raw_csv_path)
        else:
            df = self.execute_query("SELECT * FROM customer_churn_raw")
        self.validate_required_columns(df)
        return df

    def validate_required_columns(self, df: pd.DataFrame) -> bool:
        """Verify that all required columns exist in the provided DataFrame."""
        missing = [
            col for col in self.col_map.required_columns if col not in df.columns
        ]
        if missing:
            raise ValueError(f"Dataset is missing required columns: {missing}")
        return True

    def inspect_database_metadata(self) -> Dict[str, Any]:
        """Inspect SQLite database tables, row counts, and column schemas."""
        self.bootstrap_sqlite_from_csv()
        metadata: Dict[str, Any] = {
            "db_type": "SQLite (bootstrapped from uploaded Telco-Customer-Churn.csv)",
            "sqlite_version": sqlite3.sqlite_version,
            "tables": {},
        }
        with self.get_read_only_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
            tables = [row[0] for row in cursor.fetchall()]
            for tbl in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
                row_count = cursor.fetchone()[0]
                cursor.execute(f"PRAGMA table_info({tbl});")
                cols = [
                    {
                        "cid": r[0],
                        "name": r[1],
                        "type": r[2],
                        "notnull": bool(r[3]),
                        "default": r[4],
                        "pk": bool(r[5]),
                    }
                    for r in cursor.fetchall()
                ]
                metadata["tables"][tbl] = {
                    "row_count": row_count,
                    "columns": cols,
                }
        return metadata
