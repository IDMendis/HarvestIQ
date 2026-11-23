from pathlib import Path

import numpy as np
import pandas as pd

FEATURE_TABLE = Path(__file__).resolve().parents[2] / "data" / "processed" / "vegetable_prices_features.csv"
NOTEBOOK_PRICES = [313.27, 483.19, 407.38, 281.63, 355.47, 207.06, 328.11, 257.10, 176.97, 207.30]


def verify_notebook(model):
    data = pd.read_csv(FEATURE_TABLE, parse_dates=["date"])
    dates = data["date"].drop_duplicates().sort_values()
    cutoff = dates.iloc[int(len(dates) * 0.8)]
    rows = (
        data[data["date"] >= cutoff]
        .dropna(subset=["target_price_7d"])
        .sort_values(["date", "original_series"])
        .head(10)
    )
    actual = rows["price"].to_numpy() + model.predict_change(rows)
    np.testing.assert_allclose(actual, NOTEBOOK_PRICES, rtol=0, atol=0.00500001)
    np.testing.assert_array_equal(actual.round(2), NOTEBOOK_PRICES)
    print(f"Notebook prices: {actual.round(2).tolist()}")
    print(f"Max difference from the notebook's rounded values: {max(abs(actual - NOTEBOOK_PRICES)):.8f} LKR/kg")
