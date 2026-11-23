# Vegetable price forecast API

Run these commands in PowerShell with 64-bit Python 3.12:

```powershell
Set-Location 'D:\Vegetable_Price_Codex\web-app\backend'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
# Run once if artifacts/ is absent.
.\.venv\Scripts\python.exe export_model.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs for the API schema. The local React dev
origins on port 5173 are allowed.

- GET /health reports a completed startup.
- GET /api/options returns a `series` array of exact combinations with complete
  forecast inputs. Filter these tuples by vegetable and market for dependent
  selectors. Submit the original case-sensitive values.
- POST /api/predict takes one advertised combination as JSON. For example,
  `{"vegetable":"Beans","market":"pettah","price_type":"retail"}`.
- GET /api/history takes the same fields as query parameters and returns dated observations.
- GET /api/model-info reports model metadata and the latest snapshot date.

The API reads dashboard/dashboard_data.csv at startup. Forecasts use the latest
observation with complete features for the selected series and estimate a single
price seven calendar days after that observation. Unknown combinations return
404, malformed input returns 422, and a series without complete features returns 409.
The history endpoint serves observed prices.

The one-time exporter verifies the exact local source SHA-256, recovers the booster
from the known snapshot format, and uses XGBoost's native UBJSON export. The runtime
uses XGBoost's public loader and a joblib bundle of fitted scikit-learn objects.
Joblib deserialization can execute code. Keep the generated artifacts in a trusted
local directory and never accept model uploads. Manifest checksums detect accidental
changes and do not authenticate a replacement manifest. Dependencies are pinned to
the versions used for the Windows environment. The artifact directory is gitignored.

Conversion publishes the artifact directory only after reproducing the ten prices
displayed in the notebook and matching all 40 latest forecasts against the recovered
original ensemble. The exporter uses a conversion-only joblib internal class and
is limited to the exact verified source. Runtime loading uses public APIs.
