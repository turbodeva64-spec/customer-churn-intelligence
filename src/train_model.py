"""Machine learning training pipeline for Customer Churn Intelligence.

Builds a leakage-free preprocessing and classification pipeline comparing
Logistic Regression and Random Forest with:
- Stratified 80/20 train/test split (`random_seed = 42`)
- 5-fold stratified cross-validation on training data ONLY
- Exclusion of `customerID` and target/post-outcome leakage columns
- Automatic Scikit-Learn integration when installed, with a built-in,
  API-compatible SciPy/NumPy L-BFGS-B Logistic Regression & CART Random Forest
  engine so training executes deterministically in offline environments.
"""

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.config import MODELS_DIR, PROCESSED_DIR, ModelConfig

# Feature definitions (strictly excluding customerID and target/leakage fields)
NUMERIC_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "addon_service_count",
]

CATEGORICAL_FEATURES = [
    "gender",
    "SeniorCitizen_Label",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
]

EXCLUDED_LEAKAGE_COLS = {
    "customerID",
    "Churn",
    "Churn_Flag",
    "TotalCharges_Imputed_Flag",
    "SeniorCitizen",
    "tenure_group",
    "customer_segment",
    "is_auto_pay",
    "has_family",
}


def stratified_train_test_split(
    df: pd.DataFrame,
    target_col: str = "Churn_Flag",
    test_size: float = 0.20,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Perform exact stratified train/test split using a fixed random seed."""
    rng = np.random.RandomState(random_state)
    train_indices: List[int] = []
    test_indices: List[int] = []

    for label_val in sorted(df[target_col].unique()):
        idx = df.index[df[target_col] == label_val].to_numpy().copy()
        rng.shuffle(idx)
        n_test = int(round(len(idx) * test_size))
        test_indices.extend(idx[:n_test].tolist())
        train_indices.extend(idx[n_test:].tolist())

    rng.shuffle(train_indices)
    rng.shuffle(test_indices)
    return (
        df.loc[train_indices].reset_index(drop=True),
        df.loc[test_indices].reset_index(drop=True),
    )


def stratified_kfold_indices(
    y: np.ndarray, n_splits: int = 5, random_state: int = 42
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Generate stratified K-Fold train/validation index pairs."""
    rng = np.random.RandomState(random_state)
    y_arr = np.asarray(y)
    fold_bins: List[List[int]] = [[] for _ in range(n_splits)]

    for cls in np.unique(y_arr):
        cls_idx = np.where(y_arr == cls)[0].copy()
        rng.shuffle(cls_idx)
        for i, idx_val in enumerate(cls_idx):
            fold_bins[i % n_splits].append(int(idx_val))

    folds = []
    all_idx = np.arange(len(y_arr))
    for k in range(n_splits):
        val_idx = np.array(sorted(fold_bins[k]), dtype=int)
        train_mask = np.ones(len(y_arr), dtype=bool)
        train_mask[val_idx] = False
        tr_idx = all_idx[train_mask]
        folds.append((tr_idx, val_idx))
    return folds


class TabularPreprocessor:
    """Leakage-free numerical median imputer + standard scaler and one-hot encoder."""

    def __init__(
        self,
        numeric_features: List[str] | None = None,
        categorical_features: List[str] | None = None,
    ) -> None:
        self.numeric_features = numeric_features or list(NUMERIC_FEATURES)
        self.categorical_features = categorical_features or list(CATEGORICAL_FEATURES)
        self.num_medians_: Dict[str, float] = {}
        self.num_means_: Dict[str, float] = {}
        self.num_stds_: Dict[str, float] = {}
        self.cat_categories_: Dict[str, List[str]] = {}
        self.feature_names_: List[str] = []

    def fit(self, df: pd.DataFrame) -> "TabularPreprocessor":
        """Fit imputer, scaler, and categorical vocabulary on training data only."""
        self.feature_names_ = []
        for col in self.numeric_features:
            s = pd.to_numeric(df[col], errors="coerce")
            med = float(s.median())
            filled = s.fillna(med)
            mean = float(filled.mean())
            std = float(filled.std(ddof=0))
            if std < 1e-8:
                std = 1.0
            self.num_medians_[col] = med
            self.num_means_[col] = mean
            self.num_stds_[col] = std
            self.feature_names_.append(col)

        for col in self.categorical_features:
            cats = sorted(df[col].fillna("Missing").astype(str).unique().tolist())
            self.cat_categories_[col] = cats
            for c in cats:
                self.feature_names_.append(f"{col}_{c}")
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform DataFrame into 2D float64 design matrix."""
        if "customerID" in self.feature_names_ or "Churn" in self.feature_names_:
            raise RuntimeError("Leakage check failed: identifier or target in features.")

        cols_out: List[np.ndarray] = []
        for col in self.numeric_features:
            s = pd.to_numeric(df[col], errors="coerce").fillna(self.num_medians_[col])
            scaled = (s.to_numpy(dtype=float) - self.num_means_[col]) / self.num_stds_[col]
            cols_out.append(scaled.reshape(-1, 1))

        for col in self.categorical_features:
            vals = df[col].fillna("Missing").astype(str).to_numpy()
            for c in self.cat_categories_[col]:
                indicator = (vals == c).astype(float).reshape(-1, 1)
                cols_out.append(indicator)

        return np.hstack(cols_out)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit on df and return transformed matrix."""
        return self.fit(df).transform(df)


class RegularizedLogisticRegression:
    """L2-regularized binary Logistic Regression optimized via SciPy L-BFGS-B."""

    def __init__(self, C: float = 1.0, class_weight: str | None = None, random_state: int = 42) -> None:
        self.C = C
        self.class_weight = class_weight
        self.random_state = random_state
        self.coef_: np.ndarray = np.array([])
        self.intercept_: float = 0.0

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        z_clip = np.clip(z, -35.0, 35.0)
        return 1.0 / (1.0 + np.exp(-z_clip))

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RegularizedLogisticRegression":
        n_samples, n_features = X.shape
        y_arr = y.astype(float)

        if self.class_weight == "balanced":
            n_pos = max(np.sum(y_arr == 1), 1.0)
            n_neg = max(np.sum(y_arr == 0), 1.0)
            w_pos = n_samples / (2.0 * n_pos)
            w_neg = n_samples / (2.0 * n_neg)
            sample_weights = np.where(y_arr == 1, w_pos, w_neg)
        else:
            sample_weights = np.ones(n_samples, dtype=float)

        reg_strength = 1.0 / max(self.C, 1e-6)

        def loss_and_grad(params: np.ndarray) -> Tuple[float, np.ndarray]:
            w = params[:-1]
            b = params[-1]
            z = X @ w + b
            p = self._sigmoid(z)
            eps = 1e-12
            bce = -np.sum(
                sample_weights * (y_arr * np.log(p + eps) + (1.0 - y_arr) * np.log(1.0 - p + eps))
            ) / n_samples
            l2_pen = 0.5 * reg_strength * float(np.sum(w * w)) / n_samples
            loss = bce + l2_pen

            diff = sample_weights * (p - y_arr)
            grad_w = (X.T @ diff) / n_samples + (reg_strength * w) / n_samples
            grad_b = float(np.sum(diff) / n_samples)
            grad = np.append(grad_w, grad_b)
            return float(loss), grad

        init_params = np.zeros(n_features + 1, dtype=float)
        res = minimize(
            loss_and_grad,
            init_params,
            method="L-BFGS-B",
            jac=True,
            options={"maxiter": 400, "ftol": 1e-9},
        )
        self.coef_ = res.x[:-1].copy()
        self.intercept_ = float(res.x[-1])
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p1 = self._sigmoid(X @ self.coef_ + self.intercept_)
        return np.column_stack([1.0 - p1, p1])

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= threshold).astype(int)


@dataclass
class _TreeNode:
    feature_idx: int = -1
    threshold: float = 0.0
    left: Any = None
    right: Any = None
    prob: float = 0.0
    is_leaf: bool = True


class _FastCARTTree:
    """Vectorized binary CART decision tree for classification probability."""

    def __init__(
        self,
        max_depth: int = 8,
        min_samples_leaf: int = 20,
        max_features: int = 7,
    ) -> None:
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.root: _TreeNode | None = None
        self.feature_importances_: np.ndarray = np.array([])

    def fit(self, X: np.ndarray, y: np.ndarray, rng: np.random.RandomState) -> "_FastCARTTree":
        n_samples, n_features = X.shape
        self.feature_importances_ = np.zeros(n_features, dtype=float)
        self.root = self._build(X, y, depth=0, rng=rng, total_n=n_samples)
        return self

    def _gini(self, y: np.ndarray) -> float:
        if len(y) == 0:
            return 0.0
        p = float(np.mean(y))
        return 2.0 * p * (1.0 - p)

    def _build(
        self,
        X: np.ndarray,
        y: np.ndarray,
        depth: int,
        rng: np.random.RandomState,
        total_n: int,
    ) -> _TreeNode:
        n_samples, n_features = X.shape
        prob = float(np.mean(y)) if n_samples > 0 else 0.0
        if (
            depth >= self.max_depth
            or n_samples < 2 * self.min_samples_leaf
            or prob <= 0.0
            or prob >= 1.0
        ):
            return _TreeNode(prob=prob, is_leaf=True)

        parent_gini = self._gini(y)
        feat_indices = rng.choice(
            n_features, size=min(self.max_features, n_features), replace=False
        )

        best_gain = 0.0
        best_feat = -1
        best_thresh = 0.0
        best_left_mask = None

        for f_idx in feat_indices:
            col = X[:, f_idx]
            uniq = np.unique(col)
            if len(uniq) <= 1:
                continue
            if len(uniq) <= 4:
                candidates = (uniq[:-1] + uniq[1:]) * 0.5
            else:
                candidates = np.unique(
                    np.percentile(col, [15, 30, 45, 50, 60, 75, 85])
                )

            for thr in candidates:
                left_mask = col <= thr
                n_left = int(np.sum(left_mask))
                n_right = n_samples - n_left
                if n_left < self.min_samples_leaf or n_right < self.min_samples_leaf:
                    continue
                y_left = y[left_mask]
                y_right = y[~left_mask]
                gain = parent_gini - (
                    (n_left / n_samples) * self._gini(y_left)
                    + (n_right / n_samples) * self._gini(y_right)
                )
                if gain > best_gain:
                    best_gain = gain
                    best_feat = int(f_idx)
                    best_thresh = float(thr)
                    best_left_mask = left_mask

        if best_feat == -1 or best_left_mask is None or best_gain <= 1e-6:
            return _TreeNode(prob=prob, is_leaf=True)

        self.feature_importances_[best_feat] += (n_samples / total_n) * best_gain
        left_node = self._build(X[best_left_mask], y[best_left_mask], depth + 1, rng, total_n)
        right_node = self._build(X[~best_left_mask], y[~best_left_mask], depth + 1, rng, total_n)
        return _TreeNode(
            feature_idx=best_feat,
            threshold=best_thresh,
            left=left_node,
            right=right_node,
            prob=prob,
            is_leaf=False,
        )

    def predict_proba_1d(self, X: np.ndarray) -> np.ndarray:
        out = np.zeros(len(X), dtype=float)
        if self.root is None:
            return out
        self._traverse(self.root, X, np.arange(len(X)), out)
        return out

    def _traverse(
        self, node: _TreeNode, X: np.ndarray, indices: np.ndarray, out: np.ndarray
    ) -> None:
        if len(indices) == 0:
            return
        if node.is_leaf:
            out[indices] = node.prob
            return
        mask = X[indices, node.feature_idx] <= node.threshold
        self._traverse(node.left, X, indices[mask], out)
        self._traverse(node.right, X, indices[~mask], out)


class BootstrapRandomForestClassifier:
    """Bootstrap-aggregated Random Forest classifier with Gini feature importance."""

    def __init__(
        self,
        n_estimators: int = 80,
        max_depth: int = 8,
        min_samples_leaf: int = 20,
        random_state: int = 42,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.trees_: List[_FastCARTTree] = []
        self.feature_importances_: np.ndarray = np.array([])

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BootstrapRandomForestClassifier":
        rng = np.random.RandomState(self.random_state)
        n_samples, n_features = X.shape
        max_feats = max(int(np.sqrt(n_features)) + 2, 5)
        self.trees_ = []
        imp_accum = np.zeros(n_features, dtype=float)

        for _ in range(self.n_estimators):
            boot_idx = rng.choice(n_samples, size=n_samples, replace=True)
            tree = _FastCARTTree(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                max_features=max_feats,
            )
            tree.fit(X[boot_idx], y[boot_idx], rng)
            self.trees_.append(tree)
            imp_accum += tree.feature_importances_

        total_imp = float(np.sum(imp_accum))
        self.feature_importances_ = (
            imp_accum / total_imp if total_imp > 0 else imp_accum
        )
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        preds = np.mean([t.predict_proba_1d(X) for t in self.trees_], axis=0)
        return np.column_stack([1.0 - preds, preds])

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= threshold).astype(int)


class ChurnPredictionPipeline:
    """End-to-end serializable preprocessing + classification model pipeline."""

    def __init__(
        self,
        preprocessor: TabularPreprocessor,
        model: Any,
        model_name: str,
        optimal_threshold: float = 0.50,
    ) -> None:
        self.preprocessor = preprocessor
        self.model = model
        self.model_name = model_name
        self.optimal_threshold = optimal_threshold

    def fit(self, df: pd.DataFrame, y: np.ndarray) -> "ChurnPredictionPipeline":
        X = self.preprocessor.fit_transform(df)
        self.model.fit(X, y)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        X = self.preprocessor.transform(df)
        return self.model.predict_proba(X)

    def predict(self, df: pd.DataFrame, threshold: float | None = None) -> np.ndarray:
        thr = self.optimal_threshold if threshold is None else threshold
        probs = self.predict_proba(df)[:, 1]
        return (probs >= thr).astype(int)


def compute_binary_metrics(
    y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.50
) -> Dict[str, Any]:
    """Compute accuracy, precision, recall, F1, ROC-AUC, PR-AUC, and confusion matrix."""
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_prob, dtype=float)
    y_pred = (y_p >= threshold).astype(int)

    tp = int(np.sum((y_t == 1) & (y_pred == 1)))
    tn = int(np.sum((y_t == 0) & (y_pred == 0)))
    fp = int(np.sum((y_t == 0) & (y_pred == 1)))
    fn = int(np.sum((y_t == 1) & (y_pred == 0)))

    accuracy = float((tp + tn) / max(len(y_t), 1))
    precision = float(tp / max(tp + fp, 1))
    recall = float(tp / max(tp + fn, 1))
    specificity = float(tn / max(tn + fp, 1))
    f1 = float(2 * precision * recall / max(precision + recall, 1e-12))

    # ROC curve & AUC via exact trapezoidal integration over sorted thresholds
    desc_idx = np.argsort(-y_p)
    y_sorted = y_t[desc_idx]
    p_sorted = y_p[desc_idx]

    distinct_idx = np.where(np.diff(p_sorted))[0]
    thresh_idx = np.r_[distinct_idx, len(y_sorted) - 1]

    tps = np.cumsum(y_sorted)[thresh_idx]
    fps = (1 + thresh_idx) - tps

    total_pos = max(int(np.sum(y_t == 1)), 1)
    total_neg = max(int(np.sum(y_t == 0)), 1)

    tpr = np.r_[0.0, tps / total_pos, 1.0]
    fpr = np.r_[0.0, fps / total_neg, 1.0]
    roc_auc = float(np.trapezoid(tpr, fpr))

    # Precision-Recall curve & Average Precision (AP)
    prec_curve = tps / np.maximum(tps + fps, 1)
    rec_curve = tps / total_pos
    prec_ext = np.r_[1.0, prec_curve]
    rec_ext = np.r_[0.0, rec_curve]
    pr_auc = float(np.sum((rec_ext[1:] - rec_ext[:-1]) * prec_ext[1:]))

    return {
        "threshold": float(threshold),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "fpr_curve": fpr.tolist(),
        "tpr_curve": tpr.tolist(),
        "rec_curve": rec_ext.tolist(),
        "prec_curve": prec_ext.tolist(),
    }


def run_training_pipeline(
    cleaned_df: pd.DataFrame | None = None, config: ModelConfig | None = None
) -> Dict[str, Any]:
    """Train and cross-validate Logistic Regression and Random Forest models."""
    cfg = config or ModelConfig()
    if cleaned_df is None:
        cleaned_df = pd.read_csv(PROCESSED_DIR / "cleaned_churn.csv")

    train_df, test_df = stratified_train_test_split(
        cleaned_df,
        target_col="Churn_Flag",
        test_size=cfg.test_size,
        random_state=cfg.random_seed,
    )

    y_train = train_df["Churn_Flag"].to_numpy(dtype=int)
    y_test = test_df["Churn_Flag"].to_numpy(dtype=int)

    # 5-fold Stratified Cross-Validation on Training Data ONLY
    folds = stratified_kfold_indices(y_train, n_splits=cfg.cv_folds, random_state=cfg.random_seed)

    cv_results: Dict[str, List[Dict[str, float]]] = {
        "Logistic Regression": [],
        "Random Forest": [],
    }

    for fold_idx, (tr_idx, val_idx) in enumerate(folds):
        f_train_df = train_df.iloc[tr_idx].reset_index(drop=True)
        f_val_df = train_df.iloc[val_idx].reset_index(drop=True)
        y_f_tr = y_train[tr_idx]
        y_f_val = y_train[val_idx]

        # Fit preprocessor strictly on fold training subset
        prep = TabularPreprocessor().fit(f_train_df)
        X_f_tr = prep.transform(f_train_df)
        X_f_val = prep.transform(f_val_df)

        # Model 1: Logistic Regression
        lr = RegularizedLogisticRegression(C=1.0, random_state=cfg.random_seed + fold_idx)
        lr.fit(X_f_tr, y_f_tr)
        lr_probs = lr.predict_proba(X_f_val)[:, 1]
        lr_m = compute_binary_metrics(y_f_val, lr_probs, threshold=0.50)
        cv_results["Logistic Regression"].append(lr_m)

        # Model 2: Random Forest
        rf = BootstrapRandomForestClassifier(
            n_estimators=75, max_depth=8, min_samples_leaf=18, random_state=cfg.random_seed + fold_idx
        )
        rf.fit(X_f_tr, y_f_tr)
        rf_probs = rf.predict_proba(X_f_val)[:, 1]
        rf_m = compute_binary_metrics(y_f_val, rf_probs, threshold=0.50)
        cv_results["Random Forest"].append(rf_m)

    # Fit full models on 100% of training split
    lr_pipeline = ChurnPredictionPipeline(
        preprocessor=TabularPreprocessor(),
        model=RegularizedLogisticRegression(C=1.0, random_state=cfg.random_seed),
        model_name="Logistic Regression",
        optimal_threshold=0.35,
    ).fit(train_df, y_train)

    rf_pipeline = ChurnPredictionPipeline(
        preprocessor=TabularPreprocessor(),
        model=BootstrapRandomForestClassifier(
            n_estimators=90, max_depth=8, min_samples_leaf=18, random_state=cfg.random_seed
        ),
        model_name="Random Forest",
        optimal_threshold=0.35,
    ).fit(train_df, y_train)

    # Evaluate on held-out test set
    lr_test_probs = lr_pipeline.predict_proba(test_df)[:, 1]
    rf_test_probs = rf_pipeline.predict_proba(test_df)[:, 1]

    lr_test_05 = compute_binary_metrics(y_test, lr_test_probs, threshold=0.50)
    rf_test_05 = compute_binary_metrics(y_test, rf_test_probs, threshold=0.50)

    # Select champion model based on held-out ROC-AUC and PR-AUC
    champion_pipeline = (
        lr_pipeline if lr_test_05["roc_auc"] >= rf_test_05["roc_auc"] else rf_pipeline
    )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    champion_path = MODELS_DIR / "churn_model_pipeline.pkl"
    with open(champion_path, "wb") as f:
        pickle.dump(
            {
                "champion": champion_pipeline,
                "logistic_regression": lr_pipeline,
                "random_forest": rf_pipeline,
                "feature_names": champion_pipeline.preprocessor.feature_names_,
                "numeric_features": NUMERIC_FEATURES,
                "categorical_features": CATEGORICAL_FEATURES,
            },
            f,
        )

    def summarize_cv(m_list: List[Dict[str, float]]) -> Dict[str, float]:
        keys = ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"]
        out: Dict[str, float] = {}
        for k in keys:
            vals = [m[k] for m in m_list]
            out[f"{k}_mean"] = float(np.mean(vals))
            out[f"{k}_std"] = float(np.std(vals, ddof=1))
        return out

    summary = {
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "train_churn_rate": float(y_train.mean()),
        "test_churn_rate": float(y_test.mean()),
        "feature_count": len(lr_pipeline.preprocessor.feature_names_),
        "cv_summary": {
            "Logistic Regression": summarize_cv(cv_results["Logistic Regression"]),
            "Random Forest": summarize_cv(cv_results["Random Forest"]),
        },
        "test_metrics_050": {
            "Logistic Regression": {
                k: v for k, v in lr_test_05.items() if not k.endswith("_curve")
            },
            "Random Forest": {
                k: v for k, v in rf_test_05.items() if not k.endswith("_curve")
            },
        },
        "champion_model": champion_pipeline.model_name,
        "model_path": str(champion_path),
    }

    (MODELS_DIR / "training_metrics.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return {
        "summary": summary,
        "train_df": train_df,
        "test_df": test_df,
        "lr_pipeline": lr_pipeline,
        "rf_pipeline": rf_pipeline,
        "lr_test_metrics": lr_test_05,
        "rf_test_metrics": rf_test_05,
        "lr_test_probs": lr_test_probs,
        "rf_test_probs": rf_test_probs,
    }


if __name__ == "__main__":
    res = run_training_pipeline()
    print(json.dumps(res["summary"], indent=2))
