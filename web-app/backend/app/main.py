from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from .data import NoCompleteObservation, Snapshot, UnknownSeries
from .inference import Ensemble
from .schemas import Forecast, Health, History, HistoryPoint, ModelInfo, Options, SeriesSelection

BACKEND = Path(__file__).resolve().parents[1]
SNAPSHOT = BACKEND.parents[1] / "dashboard" / "dashboard_data.csv"


def create_app(snapshot_path: Path = SNAPSHOT, artifact_dir: Path = BACKEND / "artifacts") -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.ensemble = Ensemble(artifact_dir)
        app.state.snapshot = Snapshot(snapshot_path)
        yield

    app = FastAPI(title="Sri Lankan Vegetable Price Prediction", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health", response_model=Health)
    def health():
        return Health()

    @app.get("/api/options", response_model=Options)
    def options(request: Request):
        return Options(series=[
            SeriesSelection(vegetable=vegetable, market=market, price_type=price_type)
            for vegetable, market, price_type in request.app.state.snapshot.predictable
        ])

    @app.post("/api/predict", response_model=Forecast)
    def predict(selection: SeriesSelection, request: Request):
        try:
            latest = request.app.state.snapshot.latest_complete(selection.key())
        except UnknownSeries as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except NoCompleteObservation as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        change = float(request.app.state.ensemble.predict_change(latest.to_frame().T)[0])
        observation_date = latest["date"].date()
        current_price = float(latest["price"])
        return Forecast(
            **selection.model_dump(), observation_date=observation_date,
            forecast_date=observation_date + timedelta(days=7),
            observed_price=current_price, predicted_change=change,
            forecast_price=current_price + change,
        )

    @app.get("/api/history", response_model=History)
    def history(request: Request, selection: Annotated[SeriesSelection, Query()]):
        try:
            rows = request.app.state.snapshot.history(selection.key())
        except UnknownSeries as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return History(
            **selection.model_dump(),
            observations=[
                HistoryPoint(date=row.date.date(), price=row.price)
                for row in rows.dropna(subset=["price"]).itertuples(index=False)
            ],
        )

    @app.get("/api/model-info", response_model=ModelInfo)
    def model_info(request: Request):
        return ModelInfo(
            **request.app.state.ensemble.metadata,
            latest_snapshot_observation_date=request.app.state.snapshot.latest_date,
        )

    return app


app = create_app()
