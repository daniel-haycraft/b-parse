import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
from .models import Base
from . import logic

def main():
    parser = argparse.ArgumentParser(description="Correspondent Pricing Pipeline")
    parser.add_argument("--excel", required=True, help="Path to Excel workbook")
    parser.add_argument("--db", default="sqlite:///correspondent_pricing.db", help="SQLAlchemy DB URL")
    parser.add_argument("--outdir", default="out", help="Output directory for CSV/HTML")
    args = parser.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    # Load sheets
    state_df = pd.read_excel(args.excel, sheet_name="State").dropna(how="all", axis=1)
    matrix_df = pd.read_excel(args.excel, sheet_name="Matrixes w match key").dropna(how="all", axis=1)
    deals_df_raw = logic.load_data_sheet_with_header_detection(args.excel, "Data", "Record ID")
    deals_df = logic.prepare_deals(deals_df_raw)

    # DB init
    engine = create_engine(args.db)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Persist raw tables
    state_df.to_sql("states", engine, if_exists="replace", index=False)
    cols_matrix = [
        "Experience Level","Project Type","Loan Type","FICO","Number of Units",
        "Max LTAIV","Max LTC","Max LTARV","Base Rate","Loan Level Adj","Adj Rate",
        "Min Loan Amount","Max Loan Amount","Max Cash Out"
    ]
    matrix_df[cols_matrix].to_sql("pricing_matrix", engine, if_exists="replace", index=False)
    deals_df.to_sql("deals", engine, if_exists="replace", index=False)

    # Compute pricing
    results = logic.compute_pricing(deals_df, matrix_df, state_df)
    results.to_sql("pricing_results", engine, if_exists="replace", index=False)
    results.to_csv(outdir / "pricing_results.csv", index=False)

    # Render HTML via Jinja2
    env = Environment(loader=FileSystemLoader(str(Path(__file__).parent.parent / "templates")))
    template = env.get_template("report.html.jinja")
    html = template.render(rows=results.fillna("").to_dict(orient="records"))
    (outdir / "pricing_report.html").write_text(html, encoding="utf-8")

    print(f"✔ Wrote: {outdir/'pricing_results.csv'}")
    print(f"✔ Wrote: {outdir/'pricing_report.html'}")
    print(f"✔ DB URL: {args.db}")

if __name__ == "__main__":
    main()
