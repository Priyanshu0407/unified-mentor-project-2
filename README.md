# France Top 50 — Content Compliance Dashboard

This folder contains everything needed to run the Streamlit dashboard for
Atlantic Recording Corporation's Audience Sensitivity, Content Compliance &
Format Preference Analysis of the France Top 50 playlist.

## Files
- `streamlit_app.py` — the dashboard application
- `atlantic_france_clean.csv` — the validated, cleaned dataset the app reads
  (duplicates removed, dates parsed, duration converted to minutes, rank
  tiers and duration/album-size buckets pre-computed)

## Setup

```bash
pip install streamlit pandas plotly numpy
```

## Run

From this folder:

```bash
python -m streamlit run streamlit_app.py
```

This opens the dashboard at `http://localhost:8501`.

## What's inside the dashboard

- **KPI row** — Explicit Content Share, Clean Content Dominance Ratio,
  Single vs Album Ratio, Average Song Duration, Average Album Size, and a
  Content Acceptance Score, all recalculated live from the current filters.
- **Content Compliance Summary panel** — a plain-language auto-generated
  summary of the current selection.
- **Explicit vs Clean tab** — share, popularity comparison, daily trend
  line, and explicit share by rank tier.
- **Album Format tab** — format share, popularity by format, album-size
  distribution and the album-size dilution effect.
- **Song Duration tab** — duration histogram, duration buckets, popularity
  and average rank by duration bucket.
- **Rank-Tier Attributes tab** — a Top 10 / Top 25 / Top 50 content
  attribute comparison table and chart, top artists, and a filtered
  raw-data view.

## Filters (sidebar)

- **Date range** — restrict to any window within 18 May 2024–27 Nov 2025
- **Rank tier** — Top 10 / Top 25 / Top 50
- **Explicit content toggle** — Clean only / Both / Explicit only
- **Album type filter** — single / album / compilation (multi-select)

## Notes

- If you add new daily snapshots to the dataset going forward, append them
  to `atlantic_france_clean.csv` in the same schema (or re-run the cleaning
  step against the raw export) and the dashboard will pick them up
  automatically — no code changes required.
- To deploy this online (e.g. Streamlit Community Cloud), push this folder
  to a GitHub repo and point Streamlit Cloud at `streamlit_app.py`.
