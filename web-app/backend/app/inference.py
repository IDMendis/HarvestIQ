import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from xgboost import Booster

BASE_ORDER = ("Random Forest", "Gradient Boosting", "XGBoost")
FEATURES = (
    "price", "year", "month", "day", "day_of_week", "quarter", "day_of_year",
    "price_lag_1", "price_lag_7", "price_lag_14", "price_lag_30",
    "rolling_mean_7", "rolling_std_7", "rolling_mean_14", "rolling_std_14",
    "rolling_mean_30", "rolling_std_30", "price_change_1d", "price_change_pct_1d",
    "price_change_7d", "price_change_pct_7d", "price_change_14d",
    "price_change_pct_14d", "vegetable", "market", "price_type",
)
ARTIFACT_FILES = ("sklearn.joblib", "xgboost.ubj")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class Ensemble:
    def __init__(self, artifact_dir: Path):
        self.metadata = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
        if (
            self.metadata["format_version"] != 1
            or tuple(self.metadata["features"]) != FEATURES
            or tuple(self.metadata["base_order"]) != BASE_ORDER
            or self.metadata["forecast_horizon_days"] != 7
            or self.metadata["prediction_type"] != "price_change"
        ):
            raise ValueError("Unexpected ensemble manifest")
        for name in ARTIFACT_FILES:
            if sha256(artifact_dir / name) != self.metadata["sha256"][name]:
                raise ValueError(f"Checksum mismatch for {name}")
        self.components = joblib.load(artifact_dir / ARTIFACT_FILES[0])
        if tuple(self.components["preprocessor"].feature_names_in_) != FEATURES:
            raise ValueError("Fitted preprocessing feature order differs from the manifest")
        if self.components["meta_model"].n_features_in_ != len(BASE_ORDER):
            raise ValueError("Unexpected Ridge input count")
        self.booster = Booster()
        self.booster.load_model(artifact_dir / ARTIFACT_FILES[1])
        self.booster.set_param({"nthread": 1})

    def predict_change(self, rows):
        transformed = self.components["preprocessor"].transform(rows[list(FEATURES)])
        predictions = [
            self.components["Random Forest"].predict(transformed),
            self.components["Gradient Boosting"].predict(transformed),
            self.booster.inplace_predict(transformed),
        ]
        result = self.components["meta_model"].predict(np.column_stack(predictions))
        if not np.isfinite(result).all():
            raise ValueError("Ensemble returned a non-finite prediction")
        return result
