# HarvestIQ frontend

In one PowerShell terminal start the existing backend:

```powershell
Set-Location 'D:\Vegetable_Price_Codex\web-app\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal start the frontend:

```powershell
Set-Location 'D:\Vegetable_Price_Codex\web-app\frontend'
npm.cmd ci
npm.cmd run dev
```

Open http://localhost:5173. Node 24 was used for verification. The API defaults
to http://127.0.0.1:8000. To override it, copy .env.example to .env.local, edit
VITE_API_BASE_URL, then restart Vite. For a production build set the variable
before building. The backend already allows the local Vite origins on port 5173.

Run npm.cmd test and npm.cmd run build to verify the frontend.

Vite reads the original dashboard CSV and model evaluation CSV to derive dataset
coverage and evaluation tables. Rebuild after updating either CSV. Keep the
frontend in its project location so Vite can find the source files. History and
forecasts come from FastAPI. The history windows are measured from the last
observation for the selected series. Forecasts are a single point seven calendar
days after the source observation. All monetary values are shown in LKR/kg.
