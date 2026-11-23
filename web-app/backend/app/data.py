from pathlib import Path

import pandas as pd

from .inference import FEATURES

SERIES_COLUMNS = ["vegetable", "market", "price_type"]


class UnknownSeries(LookupError):
    pass


class NoCompleteObservation(LookupError):
    pass


class Snapshot:
    def __init__(self, path: Path):
        frame = pd.read_csv(path, parse_dates=["date"])
        if missing := (set(FEATURES) | {"date"}) - set(frame.columns):
            raise ValueError(f"Snapshot missing columns: {sorted(missing)}")
        if frame.empty or frame["date"].isna().any():
            raise ValueError("Snapshot must contain dated observations")
        self.series = {
            key: group.sort_values("date")
            for key, group in frame.groupby(SERIES_COLUMNS, sort=True)
        }
        self.predictable = {}
        for key, group in self.series.items():
            complete = group.dropna(subset=list(FEATURES)).sort_values("date")
            if not complete.empty:
                self.predictable[key] = complete.iloc[-1]
        self.latest_date = frame["date"].max().date()

    def history(self, key):
        if key not in self.series:
            vegetable, market, price_type = key
            raise UnknownSeries(
                f"No observations for vegetable={vegetable!r}, market={market!r}, "
                f"price_type={price_type!r}. Labels are case-sensitive. "
                "See GET /api/options for exact forecast combinations."
            )
        return self.series[key]

    def latest_complete(self, key):
        self.history(key)  # Distinguish unknown series from those lacking complete features.
        if key not in self.predictable:
            raise NoCompleteObservation("No observation has all model features for this series")
        return self.predictable[key]
