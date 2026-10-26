"""Configuration management for Customer Churn Intelligence project.

Reads connection parameters, file paths, column mappings, and modeling
hyperparameters from environment variables with safe defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

# Load .env if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_UPLOADED_CSV = Path(
    "/working_dir/c_6410b97acbcfd898/user_uploaded_files/ttl=63d/user_uploaded/Telco-Customer-Churn.csv"
)


@dataclass(frozen=True)
class DatabaseConfig:
    """Database connection configuration."""

    db_type: str = field(default_factory=lambda: os.getenv("DB_TYPE", "sqlite").lower())
    sqlite_db_path: Path = field(
        default_factory=lambda: PROJECT_ROOT
        / os.getenv("SQLITE_DB_PATH", "data/raw/telco_churn.db")
    )
    raw_csv_path: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "RAW_CSV_PATH",
                str(DEFAULT_UPLOADED_CSV)
                if DEFAULT_UPLOADED_CSV.exists()
                else str(PROJECT_ROOT / "data/raw/Telco-Customer-Churn.csv"),
            )
        )
    )
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    database: str = field(
        default_factory=lambda: os.getenv("DB_NAME", "churn_intelligence_db")
    )
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "readonly_analyst"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    schema: str = field(default_factory=lambda: os.getenv("DB_SCHEMA", "public"))
    table: str = field(default_factory=lambda: os.getenv("DB_TABLE", "customer_churn"))

    def validate(self) -> bool:
        """Validate database configuration settings."""
        supported = {"sqlite", "postgresql", "mysql", "csv"}
        if self.db_type not in supported:
            raise ValueError(
                f"Unsupported DB_TYPE '{self.db_type}'. Must be one of {supported}."
            )
        if not self.table or not self.table.replace("_", "").isalnum():
            raise ValueError(f"Invalid table identifier: '{self.table}'")
        if self.db_type in {"postgresql", "mysql"} and not self.host:
            raise ValueError("DB_HOST is required for remote relational databases.")
        return True

    def safe_summary(self) -> Dict[str, str]:
        """Return a dictionary of configuration details with secrets masked."""
        return {
            "db_type": self.db_type,
            "sqlite_db_path": str(self.sqlite_db_path),
            "raw_csv_path": str(self.raw_csv_path),
            "host": self.host,
            "port": str(self.port),
            "database": self.database,
            "user": self.user,
            "password": "***MASKED***" if self.password else "(empty)",
            "schema": self.schema,
            "table": self.table,
        }


@dataclass(frozen=True)
class ColumnMapping:
    """Configurable column mapping for Telco Customer Churn schema."""

    customer_id: str = "customerID"
    target: str = "Churn"
    tenure: str = "tenure"
    monthly_charges: str = "MonthlyCharges"
    total_charges: str = "TotalCharges"
    contract: str = "Contract"
    payment_method: str = "PaymentMethod"
    internet_service: str = "InternetService"
    senior_citizen: str = "SeniorCitizen"
    partner: str = "Partner"
    dependents: str = "Dependents"
    gender: str = "gender"
    phone_service: str = "PhoneService"
    multiple_lines: str = "MultipleLines"
    online_security: str = "OnlineSecurity"
    online_backup: str = "OnlineBackup"
    device_protection: str = "DeviceProtection"
    tech_support: str = "TechSupport"
    streaming_tv: str = "StreamingTV"
    streaming_movies: str = "StreamingMovies"
    paperless_billing: str = "PaperlessBilling"

    @property
    def required_columns(self) -> List[str]:
        """Return list of all required raw schema columns."""
        return [
            self.customer_id,
            self.gender,
            self.senior_citizen,
            self.partner,
            self.dependents,
            self.tenure,
            self.phone_service,
            self.multiple_lines,
            self.internet_service,
            self.online_security,
            self.online_backup,
            self.device_protection,
            self.tech_support,
            self.streaming_tv,
            self.streaming_movies,
            self.contract,
            self.paperless_billing,
            self.payment_method,
            self.monthly_charges,
            self.total_charges,
            self.target,
        ]


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for machine learning training and evaluation."""

    random_seed: int = field(
        default_factory=lambda: int(os.getenv("RANDOM_SEED", "42"))
    )
    test_size: float = field(
        default_factory=lambda: float(os.getenv("TEST_SIZE", "0.20"))
    )
    cv_folds: int = field(default_factory=lambda: int(os.getenv("CV_FOLDS", "5")))
    retention_cost_per_contact: float = field(
        default_factory=lambda: float(os.getenv("RETENTION_COST_PER_CONTACT", "15.0"))
    )
    retention_success_rate: float = field(
        default_factory=lambda: float(os.getenv("RETENTION_SUCCESS_RATE", "0.30"))
    )
    horizon_months: int = field(
        default_factory=lambda: int(os.getenv("HORIZON_MONTHS", "6"))
    )


#Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PREDICTIONS_DIR = DATA_DIR / "predictions"
MODELS_DIR = PROJECT_ROOT / "models"
VISUALS_DIR = PROJECT_ROOT / "visuals"
REPORTS_DIR = PROJECT_ROOT / "reports"
POWERBI_DIR = PROJECT_ROOT / "powerbi"
SQL_DIR = PROJECT_ROOT / "sql"
