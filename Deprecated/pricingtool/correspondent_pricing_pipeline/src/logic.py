import pandas as pd
import numpy as np

def load_data_sheet_with_header_detection(xlsx_path: str, sheet_name: str, key_header_text: str):
    import pandas as pd
    df_raw = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None)
    idxs = df_raw[df_raw.iloc[:,0].astype(str).str.contains(key_header_text, na=False)].index.tolist()
    header_idx = idxs[0] if idxs else 0
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=header_idx)
    df = df.dropna(axis=1, how='all').dropna(how='all')
    return df

def fico_bucket(v):
    try:
        v = float(v)
    except:
        return None
    if v >= 700: return ">=700"
    if 680 <= v <= 699: return "680 - 699"
    if 660 <= v <= 679: return "660 - 679"
    return None

def experience_bucket(n_projects):
    try:
        n = float(n_projects)
    except:
        return None
    if n >= 10: return "Institutional (10+) ($10m)"
    if 3 <= n <= 9: return "Experienced (3-9) ($5m)"
    if 0 <= n <= 2: return "No Experience (0-2) ($0m)"
    return None

def units_bucket(units):
    try:
        u = int(units)
    except:
        return None
    if u <= 4: return "<=4 Units"
    if 5 <= u <= 19: return "5-19 Units"
    return None

def project_type_map(product_type: str, budget: float, arv: float):
    if not isinstance(product_type, str): return None
    pt = product_type.strip().lower()
    if "bridge" in pt: return "Bridge (No Rehab)"
    if "fix and flip" in pt or "rehab" in pt:
        ratio = None
        try:
            if arv and arv > 0 and budget is not None:
                ratio = float(budget) / float(arv)
        except Exception:
            ratio = None
        return "Fix and Flip (Heavy Rehab)" if (ratio is not None and ratio > 0.20) else "Fix and Flip (Light Rehab)"
    return "Fix and Flip (Light Rehab)"

def loan_type_map(loan_type: str):
    if not isinstance(loan_type, str): return None
    lt = loan_type.strip().lower()
    if lt.startswith("cash out"): return "Cash Out Refinance"
    if lt.startswith("rate and term"): return "Rate and Term Refinance"
    if lt.startswith("purchase"): return "Purchase"
    return loan_type

def prepare_deals(df: pd.DataFrame) -> pd.DataFrame:
    needed_cols = [
        "Record ID","Property State","Fico",
        "Borrower Experience - Number of Projects","Number of Units",
        "Product Type","SM Loan Type",
        "Improvement Budget","ARV","Purchase Price","Requested Loan Amount"
    ]
    for c in needed_cols:
        if c not in df.columns: df[c] = np.nan
    out = df.copy()
    out["experience_bucket"] = out["Borrower Experience - Number of Projects"].apply(experience_bucket)
    out["fico_bucket"] = out["Fico"].apply(fico_bucket)
    out["units_bucket"] = out["Number of Units"].apply(units_bucket)
    out["loan_type_norm"] = out["SM Loan Type"].apply(loan_type_map)
    out["project_type_norm"] = out.apply(
        lambda r: project_type_map(r.get("Product Type"), r.get("Improvement Budget"), r.get("ARV")), axis=1
    )
    return out

def compute_pricing(deals_df: pd.DataFrame, matrix_df: pd.DataFrame, states_df: pd.DataFrame) -> pd.DataFrame:
    mcols = [
        "Experience Level","Project Type","Loan Type","FICO","Number of Units",
        "Max LTAIV","Max LTC","Max LTARV","Base Rate","Loan Level Adj","Adj Rate",
        "Min Loan Amount","Max Loan Amount","Max Cash Out"
    ]
    for mc in mcols:
        if mc not in matrix_df.columns: matrix_df[mc] = np.nan
    m_small = matrix_df[mcols].copy()

    merged = deals_df.merge(
        m_small,
        left_on=["experience_bucket","project_type_norm","loan_type_norm","fico_bucket","units_bucket"],
        right_on=["Experience Level","Project Type","Loan Type","FICO","Number of Units"],
        how="left"
    )

    def f(x):
        try: return float(x)
        except: return np.nan

    merged["purchase_price"] = merged["Purchase Price"].apply(f)
    merged["budget"] = merged["Improvement Budget"].apply(f)
    merged["arv"] = merged["ARV"].apply(f)
    merged["requested_loan"] = merged["Requested Loan Amount"].apply(f)

    merged["total_cost"] = np.where(
        merged["project_type_norm"].fillna("").str.contains("Fix and Flip"),
        merged[["purchase_price","budget"]].sum(axis=1, min_count=1),
        merged["purchase_price"]
    )

    merged["limit_ltc"] = merged["Max LTC"] * merged["total_cost"]
    merged["limit_ltarv"] = merged["Max LTARV"] * merged["arv"]
    merged["limit_ltaiv"] = merged["Max LTAIV"] * merged["purchase_price"]

    merged["matrix_min_loan"] = merged["Min Loan Amount"]
    merged["matrix_max_loan"] = merged["Max Loan Amount"]

    limits = pd.concat([
        merged["limit_ltc"], merged["limit_ltarv"], merged["limit_ltaiv"], merged["matrix_max_loan"]
    ], axis=1)
    merged["max_eligible_loan"] = limits.min(axis=1, skipna=True)

    merged["sized_loan_pre_min"] = np.where(
        merged["requested_loan"].notna() & merged["max_eligible_loan"].notna(),
        np.minimum(merged["requested_loan"], merged["max_eligible_loan"]),
        merged["max_eligible_loan"]
    )
    merged["final_sized_loan"] = np.where(
        merged["matrix_min_loan"].notna(),
        np.where(merged["sized_loan_pre_min"].notna(),
                 np.maximum(merged["sized_loan_pre_min"], merged["matrix_min_loan"]),
                 np.nan),
        merged["sized_loan_pre_min"]
    )

    merged["final_rate"] = np.where(
        merged["Adj Rate"].notna(),
        merged["Adj Rate"],
        merged["Base Rate"] + merged["Loan Level Adj"]
    )

    states_simple = states_df.rename(columns={"StateFULL":"Property State"})
    merged = merged.merge(
        states_simple[["Property State","AHL_AvailableStates","AHL_LicenseRequiredBusinessPurposeStates"]],
        on="Property State",
        how="left"
    )
    merged["eligible_state"] = merged["AHL_AvailableStates"].fillna(False).astype(bool)
    merged["matched_matrix"] = merged[["Experience Level","Project Type","Loan Type","FICO","Number of Units"]].notna().all(axis=1)
    merged["eligible_overall"] = merged["eligible_state"] & merged["matched_matrix"]

    out_cols = [
        "Record ID","Property State","eligible_overall","eligible_state","matched_matrix",
        "experience_bucket","project_type_norm","loan_type_norm","fico_bucket","units_bucket",
        "Max LTC","Max LTARV","Max LTAIV","Base Rate","Loan Level Adj","Adj Rate","final_rate",
        "Min Loan Amount","Max Loan Amount","requested_loan","limit_ltc","limit_ltarv","limit_ltaiv",
        "max_eligible_loan","final_sized_loan","AHL_LicenseRequiredBusinessPurposeStates",
        "purchase_price","budget","arv","total_cost"
    ]
    for c in out_cols:
        if c not in merged.columns: merged[c] = np.nan
    return merged[out_cols].copy()
