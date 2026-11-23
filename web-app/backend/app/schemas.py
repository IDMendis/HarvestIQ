from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

SelectionValue = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=80, pattern=r"^[A-Za-z][A-Za-z -]*$")]


class SeriesSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vegetable: SelectionValue
    market: SelectionValue
    price_type: SelectionValue

    def key(self) -> tuple[str, str, str]:
        return self.vegetable, self.market, self.price_type


class Forecast(SeriesSelection):
    observation_date: date
    forecast_date: date
    forecast_horizon_days: Literal[7] = 7
    observed_price: float
    predicted_change: float
    forecast_price: float
    units: Literal["LKR/kg"] = "LKR/kg"


class HistoryPoint(BaseModel):
    date: date
    price: float


class History(SeriesSelection):
    observations: list[HistoryPoint]
    units: Literal["LKR/kg"] = "LKR/kg"


class Options(BaseModel):
    series: list[SeriesSelection]


class Health(BaseModel):
    status: Literal["ok"] = "ok"


class ModelInfo(BaseModel):
    model_name: str
    prediction_type: Literal["price_change"]
    forecast_horizon_days: Literal[7]
    features: list[str]
    base_order: list[str]
    latest_snapshot_observation_date: date
    units: Literal["LKR/kg"] = "LKR/kg"
