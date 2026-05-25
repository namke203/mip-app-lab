# MIP_APP_LAB

Local sandbox for testing small internal web apps using Mornings in Paris sales/API data.

This project is intentionally separate from the main API project so experiments can stay quick, small, and low-risk.

## Folder Layout

```text
MIP_APP_LAB/
  apps/
    daily_sales_viewer/
    manager_ai_dashboard/
    labor_dashboard/
    vendor_cost_viewer/
  shared/
    data_loader/
    charts/
    utils/
  sample_data/
```

## App Ideas

- `daily_sales_viewer`: quick views of daily Square sales exports.
- `manager_ai_dashboard`: manager-facing summaries, alerts, and plain-English takeaways.
- `labor_dashboard`: labor hours, sales-per-labor-hour, and staffing checks.
- `vendor_cost_viewer`: vendor cost trends and simple item comparisons.

## Run the Memorial Weekend Dashboard

From the `MIP_APP_LAB` folder:

```bash
HOME=/tmp STREAMLIT_BROWSER_GATHER_USAGE_STATS=false .venv/bin/streamlit run apps/daily_sales_viewer/app.py
```

The dashboard compares Memorial Weekend 2025 and 2026 by location. It is a mobile-friendly prototype for quick manager review on phone screens, with compact KPI cards, simpler tables, and smaller charts.

It defaults to reading CSV files from:

```text
../New project 4/outputs/ad_hoc/2026-05-24_memorial_weekend_comparison/files/
```

You can also set a different folder in the app sidebar.

It only reads local CSV files. It does not call the Square API, does not use API tokens, and does not modify the API pull project or CSV generation logic.

## Data Rules

- Do not store API tokens in code.
- Do not commit real sales, labor, or vendor data.
- Keep real Square/API exports outside git.
- Use local files or sanitized sample data only.
- Keep each app small enough to test on its own.

## Recommended Workflow

1. Put raw exports in a local-only folder such as `raw_exports/` or `outputs/`.
2. Clean or sanitize a tiny example before using it as sample data.
3. Build shared loading/chart helpers in `shared/` only when more than one app needs them.
4. Keep app-specific logic inside that app folder.
5. Use `.env` locally for tokens or private settings, but never commit it.

## Notes

The `.gitignore` is set up to block common export files, spreadsheets, JSON dumps, local secrets, and cache folders.
