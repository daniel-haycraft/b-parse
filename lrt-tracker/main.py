import os
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()
# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
GOOGLE_CREDS_FILE = "service_account.json"  # Path to your Google service account JSON
SPREADSHEET_ID = os.environ.get("YOUR_GOOGLE_SHEET_ID")

BUSINESS_START = 8   # 8am
BUSINESS_END   = 17  # 5pm

# Map each sales officer (HubSpot owner ID) to their state
# You'll populate this — script will also auto-fetch from HubSpot (see fetch_sales_officers)
# Format: { "hubspot_owner_id": "AZ" }
OWNER_STATE_MAP = {}

# Timezone per state
STATE_TIMEZONE = {
    "AZ": "America/Phoenix",       # MST, no DST
    "CO": "America/Denver",
    "TX": "America/Chicago",
    "TN": "America/New_York",
    "GA": "America/New_York",
    "NC": "America/New_York",
}

# Your qualifying form IDs (pulled via separate HubSpot API call)
QUALIFYING_FORM_IDS = set()  # populated by fetch_qualifying_forms()

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

# ─────────────────────────────────────────────
# STEP 1: FETCH SALES OFFICERS + BUILD OWNER MAP
# ─────────────────────────────────────────────
def fetch_team_state_map():
    """
    Reads your Google Sheet tab 'Team State Map' to build a
    team_id -> state abbreviation lookup.
    Columns: Arizona, Colorado, Texas, Georgia, North Carolina, Tennessee
    Each column contains team IDs belonging to that state.
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds  = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet  = client.open_by_key(SPREADSHEET_ID)
    ws     = sheet.worksheet("Sales States")

    data = ws.get_all_records()  # list of dicts keyed by column header

    state_abbr = {
        "Arizona":        "AZ",
        "Colorado":       "CO",
        "Texas":          "TX",
        "Georgia":        "GA",
        "North Carolina": "NC",
        "Tennessee":      "TN",
    }

    team_state_map = {}
    for row in data:
        for state_name, abbr in state_abbr.items():
            team_id = str(row.get(state_name, "")).strip()
            if team_id:
                team_state_map[team_id] = abbr

    print(f"Loaded {len(team_state_map)} team ID → state mappings.")
    return team_state_map


def fetch_sales_officers(team_state_map):
    """
    Pulls all HubSpot owners, finds their primary team,
    and maps owner ID -> state abbreviation using team_state_map.
    """
    url  = "https://api.hubapi.com/crm/v3/owners?limit=100"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    owners = resp.json().get("results", [])

    for owner in owners:
        owner_id = str(owner["id"])
        teams    = owner.get("teams", [])

        # Get primary team first, fall back to first team in list
        primary = next((t for t in teams if t.get("primary")), teams[0] if teams else None)

        if primary:
            team_id = str(primary["id"])
            state   = team_state_map.get(team_id)
            if state:
                OWNER_STATE_MAP[owner_id] = state

    print(f"Loaded {len(OWNER_STATE_MAP)} owners with state mappings.")


# ─────────────────────────────────────────────
# STEP 2: FETCH QUALIFYING FORMS
# ─────────────────────────────────────────────
def fetch_qualifying_forms():
    """
    Pulls all HubSpot forms and filters to qualifying ones.
    Update the name filter below to match your naming convention.
    """
    url = "https://api.hubapi.com/marketing/v3/forms"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    forms = resp.json().get("results", [])

    for form in forms:
        # ⚠️ Update this filter to match your qualifying form names/IDs
        if "lead" in form.get("name", "").lower():  # example filter
            QUALIFYING_FORM_IDS.add(form["id"])

    print(f"Loaded {len(QUALIFYING_FORM_IDS)} qualifying forms.")


# ─────────────────────────────────────────────
# STEP 3: FETCH CONTACTS + OWNER HISTORY
# ─────────────────────────────────────────────
def fetch_contacts():
    """
    Pulls contacts with relevant properties and their owner assignment history.
    """
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    properties = [
        "hs_last_contacted",
        "hubspot_owner_id",
        "createdate",
        "firstname",
        "lastname",
        "email",
    ]

    contacts = []
    after = None

    while True:
        body = {
            "properties": properties,
            "limit": 100,
        }
        if after:
            body["after"] = after

        resp = requests.post(url, headers=HEADERS, json=body)
        resp.raise_for_status()
        data = resp.json()
        contacts.extend(data.get("results", []))

        paging = data.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging

    print(f"Fetched {len(contacts)} contacts.")
    return contacts


def fetch_owner_history(contact_id):
    """
    Pulls the full owner assignment history for a contact.
    Returns a sorted list of (assigned_at: datetime, owner_id: str) tuples.
    """
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/owners"
    # HubSpot stores property history via the audit log endpoint
    url = (
        f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
        f"?propertiesWithHistory=hubspot_owner_id"
    )
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    history_raw = (
        data.get("propertiesWithHistory", {})
            .get("hubspot_owner_id", [])
    )

    history = []
    for entry in history_raw:
        if entry.get("value") and entry.get("timestamp"):
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            history.append((ts, entry["value"]))

    # Sort oldest → newest
    history.sort(key=lambda x: x[0])
    return history


# ─────────────────────────────────────────────
# STEP 4: BUSINESS HOURS CALCULATION
# ─────────────────────────────────────────────
def business_hours_between(start_utc: datetime, end_utc: datetime, state: str) -> float:
    """
    Calculates business hours (Mon-Fri, 8am-5pm) between two UTC datetimes
    for a given state's timezone. Returns decimal hours.
    """
    tz_name = STATE_TIMEZONE.get(state, "America/Phoenix")
    tz = ZoneInfo(tz_name)

    start_local = start_utc.astimezone(tz)
    end_local   = end_utc.astimezone(tz)

    total_minutes = 0.0
    current = start_local

    while current < end_local:
        # Skip weekends
        if current.weekday() >= 5:  # 5=Sat, 6=Sun
            current += timedelta(days=1)
            current = current.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
            continue

        # Business day window
        biz_start = current.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
        biz_end   = current.replace(hour=BUSINESS_END,   minute=0, second=0, microsecond=0)

        # Clamp current to business window
        day_start = max(current, biz_start)
        day_end   = min(end_local, biz_end)

        if day_start < day_end:
            delta = (day_end - day_start).total_seconds() / 60
            total_minutes += delta

        # Move to next day
        current = (current + timedelta(days=1)).replace(
            hour=BUSINESS_START, minute=0, second=0, microsecond=0
        )

    hours = total_minutes / 60
    return round(hours, 2)


def format_duration(hours: float) -> str:
    """Formats decimal hours into 'Xh Ym' for leadership readability."""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m}m"


def sla_status(hours: float) -> str:
    """
    Color-coded SLA status.
    ✅ Green  = under 1 business hour
    🟡 Yellow = 1–4 business hours
    🔴 Red    = over 4 business hours
    ⬜ Grey   = no response yet
    """
    if hours is None:
        return "⬜ No Response"
    if hours <= 1:
        return "✅ Met"
    if hours <= 4:
        return "🟡 At Risk"
    return "🔴 Missed"


# ─────────────────────────────────────────────
# STEP 5: BUILD SLA ROWS
# ─────────────────────────────────────────────
def build_sla_rows(contacts):
    """
    For each contact, generates one SLA row per owner assignment.
    Each row = one SLA event.
    """
    rows = []

    for contact in contacts:
        contact_id  = contact["id"]
        props       = contact.get("properties", {})
        first_name  = props.get("firstname", "")
        last_name   = props.get("lastname", "")
        email       = props.get("email", "")
        last_contacted_raw = props.get("hs_last_contacted")

        last_contacted = None
        if last_contacted_raw:
            last_contacted = datetime.fromisoformat(
                last_contacted_raw.replace("Z", "+00:00")
            )

        # Get full owner assignment history
        owner_history = fetch_owner_history(contact_id)

        for i, (assigned_at, owner_id) in enumerate(owner_history):
            state = OWNER_STATE_MAP.get(owner_id, "AZ")  # default AZ if unknown

            # Next assignment time (clock stops if owner changes again)
            next_assignment = owner_history[i + 1][0] if i + 1 < len(owner_history) else None

            # First hs_last_contacted AFTER this assignment and BEFORE next assignment
            response_time = None
            if last_contacted and last_contacted >= assigned_at:
                if next_assignment is None or last_contacted < next_assignment:
                    response_time = last_contacted

            # Calculate business hours
            biz_hours = None
            if response_time:
                biz_hours = business_hours_between(assigned_at, response_time, state)

            tz_name = STATE_TIMEZONE.get(state, "America/Phoenix")
            tz = ZoneInfo(tz_name)

            rows.append({
                "Contact ID":           contact_id,
                "Name":                 f"{first_name} {last_name}".strip(),
                "Email":                email,
                "Owner ID":             owner_id,
                "Owner State":          state,
                "Timezone":             tz_name,
                "Assignment #":         i + 1,
                "Assigned At (Local)":  assigned_at.astimezone(tz).strftime("%Y-%m-%d %H:%M"),
                "Responded At (Local)": response_time.astimezone(tz).strftime("%Y-%m-%d %H:%M") if response_time else "—",
                "Business Hrs to Respond": format_duration(biz_hours) if biz_hours is not None else "—",
                "Raw Hours":            biz_hours if biz_hours is not None else "",
                "SLA Status":           sla_status(biz_hours),
            })

    print(f"Built {len(rows)} SLA rows.")
    return rows


# ─────────────────────────────────────────────
# STEP 6: WRITE TO GOOGLE SHEETS
# ─────────────────────────────────────────────
def write_to_sheets(rows):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds  = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet  = client.open_by_key(SPREADSHEET_ID)

    # ── DATA TAB ──────────────────────────────
    try:
        data_ws = sheet.worksheet("SLA Data")
        data_ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        data_ws = sheet.add_worksheet(title="SLA Data", rows=5000, cols=20)

    if rows:
        headers = list(rows[0].keys())
        values  = [headers] + [[r.get(h, "") for h in headers] for r in rows]
        data_ws.update("A1", values)

        # Header row formatting
        data_ws.format("A1:L1", {
            "backgroundColor": {"red": 0.15, "green": 0.15, "blue": 0.15},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER"
        })

        # Color SLA status column (col L = index 12)
        for i, row in enumerate(rows, start=2):
            status = row["SLA Status"]
            if "✅" in status:
                bg = {"red": 0.85, "green": 1.0,  "blue": 0.85}
            elif "🟡" in status:
                bg = {"red": 1.0,  "green": 0.95, "blue": 0.7}
            elif "🔴" in status:
                bg = {"red": 1.0,  "green": 0.8,  "blue": 0.8}
            else:
                bg = {"red": 0.93, "green": 0.93, "blue": 0.93}

            data_ws.format(f"L{i}", {"backgroundColor": bg})

    # ── DEFINITIONS TAB ───────────────────────
    try:
        def_ws = sheet.worksheet("📖 Definitions")
        def_ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        def_ws = sheet.add_worksheet(title="📖 Definitions", rows=50, cols=3)

    definitions = [
        ["Field", "Definition", "Example"],
        ["Contact ID",              "Unique HubSpot ID for the contact (lead).", "12345678"],
        ["Name",                    "Full name of the lead.", "Jane Smith"],
        ["Email",                   "Lead's email address.", "jane@example.com"],
        ["Owner ID",                "HubSpot ID of the sales rep assigned to this lead.", "98765"],
        ["Owner State",             "The state the sales rep operates in. Used to apply the correct business hours timezone.", "AZ"],
        ["Timezone",                "Timezone applied when calculating business hours for this rep's state.", "America/Phoenix"],
        ["Assignment #",            "Which assignment this row represents. If a lead changed owners 3 times, there will be 3 rows.", "2"],
        ["Assigned At (Local)",     "Date and time the rep was assigned this lead, in their local timezone.", "2024-03-01 09:00"],
        ["Responded At (Local)",    "Date and time the rep first contacted the lead (via email, call, or SMS), in their local timezone.", "2024-03-01 10:30"],
        ["Business Hrs to Respond", "Total time to respond counting only Mon–Fri business hours (8am–5pm local). Weekends and after-hours are excluded.", "1h 30m"],
        ["Raw Hours",               "Same as above but as a decimal number. Used for sorting and averages.", "1.5"],
        ["SLA Status",              "How the response time compares to your SLA target.", ""],
        ["  ✅ Met",                 "Responded within 1 business hour. Great job.", ""],
        ["  🟡 At Risk",             "Responded between 1–4 business hours. Needs attention.", ""],
        ["  🔴 Missed",              "Took longer than 4 business hours to respond. Follow up required.", ""],
        ["  ⬜ No Response",         "No response has been logged yet for this assignment.", ""],
    ]

    def_ws.update("A1", definitions)
    def_ws.format("A1:C1", {
        "backgroundColor": {"red": 0.15, "green": 0.15, "blue": 0.15},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
    })
    def_ws.format("A13:A16", {"textFormat": {"bold": True}})

    print("✅ Google Sheet updated successfully.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print(fetch_team_state_map())
    # fetch_qualifying_forms()
    # contacts = fetch_contacts()
    # rows     = build_sla_rows(contacts)
    # write_to_sheets(rows)