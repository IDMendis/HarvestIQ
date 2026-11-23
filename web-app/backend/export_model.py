"""One-time conversion of the verified local Colab artifact."""
import io
import json
import tempfile
import zlib
from pathlib import Path

import joblib
import numpy as np
from joblib.numpy_pickle import NumpyUnpickler
from threadpoolctl import threadpool_limits
from xgboost import Booster

from app.data import Snapshot
from app.inference import ARTIFACT_FILES, BASE_ORDER, FEATURES, Ensemble, sha256
from app.main import BACKEND, SNAPSHOT
from parity import verify_notebook

SOURCE = BACKEND.parents[1] / "models" / "vegetable_price_stacking.joblib"
SOURCE_SHA256 = "6f1fd2f3b9cff3254ec1247785acbf1281910de018e4b7788619ac8a523d57e4"
DESTINATION = BACKEND / "artifacts"


class SnapshotBooster(Booster):
    def __setstate__(self, state):
        # XGBoost's snapshot wraps native UBJSON in a top-level Config and Model object.
        # The verified source has Model last. Remove the outer closing delimiter.
        handle = state["handle"]
        marker = b"L" + (5).to_bytes(8, "big") + b"Model{"
        if not handle.startswith(b"{L" + (6).to_bytes(8, "big") + b"Config{") or not handle.endswith(b"}}"):
            raise ValueError("Unexpected XGBoost snapshot layout")
        model_start = handle.index(marker) + len(marker) - 1
        super().__init__()
        self.load_model(bytearray(handle[model_start:-1]))


class RecoveryUnpickler(NumpyUnpickler):
    def find_class(self, module, name):
        if (module, name) == ("xgboost.core", "Booster"):
            return SnapshotBooster
        return super().find_class(module, name)


def main():
    if DESTINATION.exists():
        raise FileExistsError(f"Export already exists at {DESTINATION}")
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("Source is not the exact trusted model inspected for this project")
    with io.BytesIO(zlib.decompress(SOURCE.read_bytes())) as stream:
        source = RecoveryUnpickler(str(SOURCE), stream, ensure_native_byte_order=True).load()
    if tuple(source["feature_columns"]) != FEATURES or tuple(source["base_models"]) != BASE_ORDER:
        raise ValueError("The original bundle has unexpected feature or base-model order")
    base = source["base_models"]
    original_booster = base["XGBoost"].get_booster()
    if original_booster.attr("best_iteration") is not None or not np.isnan(base["XGBoost"].missing):
        raise ValueError("Native prediction defaults do not match the fitted XGBoost estimator")
    original_booster.set_param({"nthread": 1})
    components = {
        "preprocessor": source["preprocessor"],
        "meta_model": source["meta_model"],
        **{name: base[name] for name in BASE_ORDER[:2]},
    }
    snapshot = Snapshot(SNAPSHOT)
    with tempfile.TemporaryDirectory(dir=BACKEND, prefix="export-check-") as temporary:
        output = Path(temporary) / "artifacts"
        output.mkdir()
        joblib.dump(components, output / ARTIFACT_FILES[0], compress=3)
        original_booster.save_model(output / ARTIFACT_FILES[1])
        manifest = {
            "format_version": 1,
            "model_name": source["model_name"],
            "prediction_type": source["prediction_type"],
            "forecast_horizon_days": source["forecast_horizon_days"],
            "features": list(FEATURES),
            "base_order": list(BASE_ORDER),
            "source_sha256": SOURCE_SHA256,
            "sha256": {name: sha256(output / name) for name in ARTIFACT_FILES},
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        with threadpool_limits(limits=1):
            model = Ensemble(output)
            verify_notebook(model)
            if len(snapshot.series) != 40:
                raise ValueError("Expected 40 series in the original dashboard snapshot")
            differences = []
            for key in snapshot.series:
                row = snapshot.latest_complete(key).to_frame().T
                transformed = source["preprocessor"].transform(row[list(FEATURES)])
                expected = source["meta_model"].predict(np.column_stack([
                    base[name].predict(transformed) for name in BASE_ORDER
                ]))
                actual = model.predict_change(row)
                np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-8)
                differences.append(float(abs(actual[0] - expected[0])))
            print(f"40 series passed. Maximum change difference: {max(differences):.12g} LKR/kg")
        output.rename(DESTINATION)


if __name__ == "__main__":
    main()
