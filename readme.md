# Week 7 — HSE Safety Dashboard

Part A technical challenge deliverable: a Streamlit dashboard for exploring HSE
incident data across a 7-site depot network in Kenya (Jan-Jun 2026, 445 records).
Incident types include slips/trips, manual handling, struck-by, vehicle
interaction, chemical exposure, and equipment contact — general workplace/depot
safety incidents, not medical or hospital data.

## What's here

```
week7_app_safety/
├── app_safety_dashboard.py     # the Streamlit app — run this
├── requirements.txt
└── data/
    └── safety_incidents_kenya.csv   # incident dataset the app reads
```

## How to run it

**1. Make sure you have Python 3.9+ installed.** Check with:
```bash
python3 --version
```

**2. (Recommended) Create and activate a virtual environment**, so this doesn't
install packages system-wide:
```bash
python3 -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the app** — must be run from the folder containing `app_safety_dashboard.py`,
since it looks for `data/safety_incidents_kenya.csv` as a relative path:
```bash
streamlit run app_safety_dashboard.py
```

**5. It should open automatically in your browser** at `http://localhost:8501`.
If it doesn't open automatically, copy that URL into your browser manually.

To stop the app, go back to the terminal and press `Ctrl+C`.

## Using the dashboard

- **Sidebar filters** (left panel): Site, Date range, Incident Type, and a
  slider for the critical-incident alert threshold. Every chart and KPI card
  updates live when you change these.
- **KPI cards** (top row): Total Incidents, Avg Severity, Critical Incidents,
  Potential SIF Events — red background means that metric is in a "bad" state
  by the thresholds documented as comments in the code.
- **Warning banners**: appear automatically if critical incidents exceed your
  chosen threshold, or if any potential-SIF event is in the filtered view.
- **Charts**: incident trend over time, breakdown by type, a map of incident
  locations by depot, and a shift/day-of-week heatmap.
- **Bottom of the page**: the filtered data table plus a CSV download button —
  exports exactly what's currently filtered, not the full dataset.

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | You skipped `pip install -r requirements.txt`, or your virtual environment isn't activated |
| `ERROR: Could not open requirements file` | `requirements.txt` isn't in your current folder — check with `dir` (Windows) or `ls` (Mac/Linux) and move/download it there |
| `FileNotFoundError` for the CSV | The CSV must be inside a `data\` subfolder next to the script, not in the project root — check with `dir` / `ls` |
| Port 8501 already in use | Another Streamlit app is running; stop it, or run `streamlit run app_safety_dashboard.py --server.port 8502` |
| Map doesn't render | Needs `plotly>=5.20` (in requirements.txt) for `px.scatter_map` — run `pip install -r requirements.txt --upgrade` |

## Swapping in a different dataset

Point `DATA_PATH` near the top of `app_safety_dashboard.py` at a different CSV.
It needs at minimum these columns: `event_id`, `incident_date`, `site`,
`incident_type`, `severity`, `shift`, `latitude`, `longitude`. Optional columns
used for extra context: `potential_sif`, `critical_control_verified`,
`incident_time`.