"""Train a crop recommendation model using regional climate data."""

from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "data" / "crop_recommendations.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "crop_recommender.pkl"
METRICS_PATH = MODEL_DIR / "crop_recommender_metrics.json"


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    return pd.read_csv(path)


def build_pipeline(categorical_features):
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            )
        ],
        remainder="passthrough",
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
    )

    return Pipeline([
        ("preprocess", preprocessor),
        ("model", model),
    ])


def train_model():
    df = load_dataset(DATA_PATH)
    target_col = "recommended_crop"

    feature_cols = [col for col in df.columns if col != target_col]

    categorical_cols = [
        "region",
        "state",
        "climate_zone",
        "primary_season",
        "monsoon_intensity",
        "soil_type",
        "irrigation",
        "wind_risk",
        "drought_risk",
        "flood_risk",
    ]

    X = df[feature_cols]
    y = df[target_col]

    # Use k-fold cross-validation for small datasets
    # n_splits cannot exceed the minimum class frequency
    min_class_freq = y.value_counts().min()
    n_splits = max(2, min(3, min_class_freq))
    kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    pipeline = build_pipeline(categorical_cols)
    
    # Use cross-validation predictions for metrics
    y_pred = cross_val_predict(pipeline, X, y, cv=kfold)
    accuracy = accuracy_score(y, y_pred)
    report = classification_report(y, y_pred, output_dict=True, zero_division=0)
    matrix = confusion_matrix(y, y_pred, labels=sorted(y.unique()))

    # Fit final model on entire dataset
    pipeline.fit(X, y)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    metrics = {
        "accuracy": accuracy,
        "classification_report": report,
        "confusion_matrix_labels": sorted(y.unique()),
        "confusion_matrix": matrix.tolist(),
        "train_samples": int(len(X)),
        "test_samples": int(len(X)),
        "cv_folds": kfold.get_n_splits(),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model saved to {MODEL_PATH}")
    print(f"Metrics saved to {METRICS_PATH}")
    print(f"CV Accuracy: {accuracy:.3f}")
    print(f"Classes: {sorted(y.unique())}")


if __name__ == "__main__":
    train_model()
