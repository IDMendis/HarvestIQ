from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from threadpoolctl import threadpool_limits

from app.data import NoCompleteObservation, Snapshot
from app.inference import BASE_ORDER, FEATURES
from app.main import SNAPSHOT, app, create_app
from parity import verify_notebook


@pytest.fixture(scope="module")
def client():
    with threadpool_limits(limits=1), TestClient(app) as client:
        yield client


def test_artifacts_and_notebook_predictions(client):
    ensemble = app.state.ensemble
    assert len(FEATURES) == 26
    assert tuple(ensemble.components["preprocessor"].feature_names_in_) == FEATURES
    assert tuple(ensemble.metadata["base_order"]) == BASE_ORDER
    verify_notebook(ensemble)


def test_metadata_and_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    response = client.get("/api/model-info")
    assert response.status_code == 200
    assert response.json()["forecast_horizon_days"] == 7
    assert response.json()["features"] == list(FEATURES)
    assert response.json()["latest_snapshot_observation_date"] == "2026-11-20"


def test_every_available_series(client):
    options = client.get("/api/options")
    assert options.status_code == 200
    series = options.json()["series"]
    columns = ["vegetable", "market", "price_type"]
    csv_combinations = pd.read_csv(SNAPSHOT, usecols=columns)[columns].drop_duplicates()
    assert len(series) == len(csv_combinations) == 40
    assert {tuple(option[column] for column in columns) for option in series} == set(
        csv_combinations.itertuples(index=False, name=None)
    )
    for selection in series:
        response = client.post("/api/predict", json=selection)
        assert response.status_code == 200, response.text
        forecast = response.json()
        assert forecast["units"] == "LKR/kg"
        assert date.fromisoformat(forecast["forecast_date"]) - date.fromisoformat(forecast["observation_date"]) == timedelta(days=7)
        assert np.isfinite(forecast["forecast_price"])
        assert forecast["forecast_price"] == pytest.approx(forecast["observed_price"] + forecast["predicted_change"])
        assert forecast["forecast_horizon_days"] == 7


def test_known_forecast_history_and_cors(client):
    selection = {"vegetable": "Tomato", "market": "pettah", "price_type": "wholesale"}
    prediction = client.post("/api/predict", json=selection)
    assert prediction.status_code == 200, prediction.text
    forecast = prediction.json()
    assert forecast["observation_date"] == "2026-11-20"
    assert forecast["forecast_price"] == pytest.approx(419.89208907967827)
    response = client.get("/api/history", params=selection, headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    points = response.json()["observations"]
    assert points[-1] == {"date": "2026-11-20", "price": 400.0}
    assert [p["date"] for p in points] == sorted(p["date"] for p in points)


def test_beans_pettah_retail_preserves_snapshot_labels(client):
    selection = {"vegetable": "Beans", "market": "pettah", "price_type": "retail"}
    response = client.post("/api/predict", json=selection)
    assert response.status_code == 200, response.text
    assert {field: response.json()[field] for field in selection} == selection


@pytest.mark.parametrize(("market", "price_type"), [
    ("Pettah", "retail"),
    ("narahenpita", "wholesale"),
])
def test_unsupported_combination_explains_exact_labels(client, market, price_type):
    response = client.post("/api/predict", json={
        "vegetable": "Beans", "market": market, "price_type": price_type,
    })
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert f"vegetable='Beans', market={market!r}, price_type={price_type!r}" in detail
    assert "case-sensitive" in detail
    assert "GET /api/options" in detail


def test_input_errors(client):
    missing = {"vegetable": "Tomato", "market": "unavailable", "price_type": "wholesale"}
    assert client.post("/api/predict", json=missing).status_code == 404
    assert client.get("/api/history", params=missing).status_code == 404
    assert client.post("/api/predict", json={**missing, "vegetable": 42}).status_code == 422
    assert client.post("/api/predict", json={"vegetable": "Tomato"}).status_code == 422
    assert client.get("/api/history", params={"vegetable": "Tomato"}).status_code == 422


def test_row_selection_skips_incomplete_rows(tmp_path):
    data = pd.read_csv(SNAPSHOT)
    rows = data.loc[(data.vegetable == "Tomato") & (data.market == "pettah") & (data.price_type == "wholesale")]
    recent = rows.dropna(subset=list(FEATURES)).sort_values("date").tail(2).copy()
    recent.loc[recent.index[-1], "price_lag_1"] = np.nan
    path = tmp_path / "snapshot.csv"
    recent.to_csv(path, index=False)
    key = ("Tomato", "pettah", "wholesale")
    assert Snapshot(path).latest_complete(key)["date"].date().isoformat() == recent.iloc[0]["date"]
    recent.tail(1).to_csv(path, index=False)
    with pytest.raises(NoCompleteObservation):
        Snapshot(path).latest_complete(key)
    with TestClient(create_app(snapshot_path=path)) as incomplete_client:
        assert incomplete_client.get("/api/options").json() == {"series": []}
        response = incomplete_client.post("/api/predict", json={
            "vegetable": key[0], "market": key[1], "price_type": key[2],
        })
        assert response.status_code == 409
