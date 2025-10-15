# Correspondent Pricing Pipeline (SQLAlchemy + Jinja2)

This minimal project converts your Excel-based correspondent pricing model into a Python pipeline that:
1) Loads & normalizes workbook sheets
2) Stores them in a SQLite/Postgres DB via **SQLAlchemy**
3) Computes eligibility + pricing by matching deals to the pricing matrix
4) Renders a per-deal HTML report using **Jinja2**

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.app \
  --excel "Correspondent Pricing Model V3 09.02.2025.xlsx" \
  --db "sqlite:///correspondent_pricing.db" \
  --outdir "out"
```

Outputs:
- `out/pricing_results.csv` – sized loan and rate for each Record ID
- `out/pricing_report.html` – nicely formatted HTML report


## Notes

- The pipeline infers headers in **Data** and **Data Validation** where the sheet contains formatted rows above the header.
- The **project type** (light vs heavy) is determined by a simple heuristic: `Improvement Budget / ARV > 20% => Heavy`. Adjust in `src/logic.py` as needed.
- The **experience bucket** and **FICO bucket** are mapped to the ranges used in your `Matrixes w match key` sheet.
- State eligibility is taken from the **State** sheet (`AHL_AvailableStates`).

If you prefer Postgres or another DB, change the `--db` string (e.g., `postgresql+psycopg://user:pass@host/dbname`) and ensure the driver is installed.
