"""
Store Management page.

Lets non-technical users add, update, and delete stores per company.
Custom stores are saved to custom_stores.json and auto-committed to GitHub
(token in Streamlit secrets), so they survive Streamlit Cloud redeploys.
config.py merges the JSON overlay into COMPANY_CONFIGS / LOCATION_MAP /
FILE_DATE_FORMATS / STORE_OPS_LINKS at load time.
"""
import base64
import calendar
import json
import os

import requests
import streamlit as st

from config import BUILTIN_LOCATION_MAP, BUILTIN_STORE_NAMES, CUSTOM_STORES_FILE, load_custom_stores

# First digit of the fingerprint filename identifies the company.
COMPANY_DIGITS = {
    "D&H": "1",
    "D&co": "2",
    "Second Cup": "3",
    "Al-hadabah times": "4",
    "D&CO Jordan": "5",
}

# Human labels -> strptime formats offered in the form.
DATE_FORMAT_OPTIONS = {
    "Day/Month/Year  (e.g. 25/06/2026 09:30:00 AM)": "%d/%m/%Y %I:%M:%S %p",
    "Month/Day/Year  (e.g. 06/25/2026 09:30:00 AM)": "%m/%d/%Y %I:%M:%S %p",
    "Day-Mon-Year  (e.g. 25-Jun-26 09:30:00 AM)": "%d-%b-%y %I:%M:%S %p",
    "Day/Month/2-digit Year  (e.g. 25/06/26 09:30:00 AM)": "%d/%m/%y %I:%M:%S %p",
}

WEEKDAYS = [
    ("Monday", calendar.MONDAY),
    ("Tuesday", calendar.TUESDAY),
    ("Wednesday", calendar.WEDNESDAY),
    ("Thursday", calendar.THURSDAY),
    ("Friday", calendar.FRIDAY),
    ("Saturday", calendar.SATURDAY),
    ("Sunday", calendar.SUNDAY),
]

GITHUB_REPO = "TheOther-Guy/FIG-D-H"
GITHUB_BRANCH = "main"
GITHUB_FILE_PATH = "custom_stores.json"


# ----------------------------------------------------------------------
# Persistence helpers
# ----------------------------------------------------------------------

def _get_github_token():
    """Reads the GitHub token from Streamlit secrets; None if not configured."""
    try:
        return st.secrets["GITHUB_TOKEN"]
    except Exception:
        return None


def _save_custom_stores(data: dict) -> tuple[bool, str]:
    """
    Writes the overlay locally and pushes it to GitHub when a token exists.

    Returns (pushed_to_github, message).
    """
    content_str = json.dumps(data, indent=2, ensure_ascii=False)
    with open(CUSTOM_STORES_FILE, "w", encoding="utf-8") as f:
        f.write(content_str)

    token = _get_github_token()
    if not token:
        return False, (
            "Saved locally only — no GITHUB_TOKEN found in Streamlit secrets. "
            "On Streamlit Cloud this change will be LOST on the next restart. "
            "Ask the administrator to add the token, or commit custom_stores.json to GitHub manually."
        )

    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    try:
        # Need the current file SHA to update it (absent on first creation).
        sha = None
        resp = requests.get(api_url, headers=headers, params={"ref": GITHUB_BRANCH}, timeout=20)
        if resp.status_code == 200:
            sha = resp.json().get("sha")

        payload = {
            "message": "Update custom stores via Store Management page",
            "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
            "branch": GITHUB_BRANCH,
        }
        if sha:
            payload["sha"] = sha
        put_resp = requests.put(api_url, headers=headers, json=payload, timeout=20)
        if put_resp.status_code in (200, 201):
            return True, "Saved and pushed to GitHub. The live app will update in a minute or two."
        return False, (
            f"Saved locally, but the GitHub push failed (HTTP {put_resp.status_code}). "
            "Check the token's permissions. On Streamlit Cloud this change may be lost on restart."
        )
    except requests.RequestException as e:
        return False, f"Saved locally, but could not reach GitHub: {e}"


# ----------------------------------------------------------------------
# Store number helpers
# ----------------------------------------------------------------------

def _used_codes(company: str, custom: dict) -> set:
    """All 2-digit location codes in use for a company (config.py + custom)."""
    codes = set(str(c) for c in BUILTIN_LOCATION_MAP.get(company, {}).values())
    for store in custom.get(company, {}).values():
        codes.add(str(store.get("code", "")))
    return codes


def _next_free_code(company: str, custom: dict) -> str:
    used = _used_codes(company, custom)
    for n in range(1, 100):
        code = f"{n:02d}"
        if code not in used:
            return code
    raise ValueError("No free location codes left for this company (max 99).")


def _file_number(company: str, code: str) -> str:
    return f"{COMPANY_DIGITS[company]}{code}"


# ----------------------------------------------------------------------
# Page
# ----------------------------------------------------------------------

def _name_taken(name: str, custom: dict) -> str | None:
    """Returns the owning company if the name is already used anywhere, else None.

    Case-insensitive, across all companies, because date formats and Google
    Sheet links are looked up by store name alone.
    """
    target = name.strip().lower()
    for company, stores in BUILTIN_LOCATION_MAP.items():
        if any(n.lower() == target for n in stores):
            return company
    for company, stores in custom.items():
        if any(n.lower() == target for n in stores):
            return company
    if any(n.lower() == target for n in BUILTIN_STORE_NAMES):
        return "config.py"
    return None


def _flash(level: str, text: str):
    """Queues a message to show after the page reloads with fresh data."""
    st.session_state.setdefault("sm_flash", []).append((level, text))


def store_management_page():
    st.title("🏪 Store Management")
    st.info(
        "Add a new store here so the app knows how to read its fingerprint files. "
        "After adding, you will get the **store number** — rename the fingerprint "
        "files to that number (e.g. `141.xlsx`) before uploading them."
    )

    for level, text in st.session_state.pop("sm_flash", []):
        getattr(st, level)(text)

    custom = load_custom_stores()

    company = st.selectbox("1️⃣ Select the company:", list(COMPANY_DIGITS.keys()), key="sm_company")

    # ------------------------------------------------------------------
    # Existing stores overview
    # ------------------------------------------------------------------
    custom_stores = custom.get(company, {})
    with st.expander("📋 Existing stores for this company", expanded=False):
        rows = []
        for name, code in sorted(BUILTIN_LOCATION_MAP.get(company, {}).items(), key=lambda x: x[1]):
            rows.append({"Store": name, "File number": _file_number(company, str(code)), "Source": "built-in"})
        for name, s in sorted(custom_stores.items(), key=lambda x: x[1].get("code", "")):
            rows.append({"Store": name, "File number": _file_number(company, str(s.get("code"))), "Source": "added here"})
        if rows:
            st.table(rows)
        else:
            st.write("No stores yet for this company.")

    # ------------------------------------------------------------------
    # Add / Update
    # ------------------------------------------------------------------
    st.subheader("➕ Add a new store or ✏️ update one added here")

    editable_names = sorted(custom_stores.keys())
    mode = st.radio(
        "What do you want to do?",
        ["Add a new store", "Update an existing store"],
        horizontal=True,
        key="sm_mode",
    )

    editing_name = None
    existing = {}
    if mode == "Update an existing store":
        if not editable_names:
            st.info(f"No stores have been added for {company} yet — choose 'Add a new store'.")
            return
        editing_name = st.selectbox("Store to update:", editable_names, key=f"sm_edit_store_{company}")
        existing = custom_stores.get(editing_name, {})

    hours_options = [8, 9] + ([12, 24] if company == "Second Cup" else [])
    # Widget keys include the store being edited so its saved values load fresh.
    form_id = f"{company}_{editing_name or '__new__'}_{st.session_state.get('sm_form_gen', 0)}"

    with st.form(f"store_form_{form_id}"):
        name = st.text_input(
            "2️⃣ Store name (exactly as the team knows it):",
            value=editing_name or "",
            disabled=editing_name is not None,
            key=f"sm_name_{form_id}",
        )

        fmt_labels = list(DATE_FORMAT_OPTIONS.keys())
        fmt_default = 0
        if existing.get("date_format") in DATE_FORMAT_OPTIONS.values():
            fmt_default = list(DATE_FORMAT_OPTIONS.values()).index(existing["date_format"])
        fmt_label = st.selectbox(
            "3️⃣ Date format of the fingerprint machine's export:",
            fmt_labels, index=fmt_default, key=f"sm_fmt_{form_id}",
        )

        hours_default = hours_options.index(existing["working_hours"]) if existing.get("working_hours") in hours_options else 0
        working_hours = st.radio(
            "4️⃣ Working hours:", hours_options, index=hours_default,
            horizontal=True, key=f"sm_hours_{form_id}",
        )
        if company == "Second Cup":
            st.caption("12 and 24 are the store's opening hours (24 enables the 24-hour shift logic).")

        st.write("5️⃣ Weekend days (check the store's days off — leave all unchecked for rotational offs):")
        existing_weekends = set(existing.get("weekend_days", []))
        cols = st.columns(7)
        weekend_days = []
        for col, (label, day_idx) in zip(cols, WEEKDAYS):
            with col:
                if st.checkbox(label[:3], value=day_idx in existing_weekends, key=f"sm_wd_{form_id}_{label}"):
                    weekend_days.append(day_idx)

        store_ops_link = st.text_input(
            "6️⃣ Google Sheet schedule link (optional — needed for the Store Ops checks):",
            value=existing.get("store_ops_link", ""),
            placeholder="https://docs.google.com/spreadsheets/d/.../export?format=csv",
            key=f"sm_link_{form_id}",
        )

        submitted = st.form_submit_button("💾 Save store", type="primary")

    if submitted:
        name = name.strip() if editing_name is None else editing_name
        if not name:
            st.error("Please enter the store name.")
            return
        if editing_name is None:
            owner = _name_taken(name, custom)
            if owner:
                st.error(
                    f"A store named '{name}' already exists ({owner}). Store names must be unique "
                    f"across all companies — add a distinguishing word, e.g. '{name} Jordan'."
                )
                return

        if editing_name is not None:
            code = existing.get("code")
        else:
            try:
                code = _next_free_code(company, custom)
            except ValueError as e:
                st.error(str(e))
                return

        custom.setdefault(company, {})[name] = {
            "code": code,
            "date_format": DATE_FORMAT_OPTIONS[fmt_label],
            "working_hours": working_hours,
            "weekend_days": sorted(weekend_days),
            "store_ops_link": store_ops_link.strip(),
        }
        pushed, message = _save_custom_stores(custom)
        _flash("success" if pushed else "warning", message)

        number = _file_number(company, code)
        action = "updated" if editing_name else "added"
        _flash(
            "success",
            f"✅ Store **{name}** {action} for **{company}**.\n\n"
            f"### 🔢 Its store number is **{number}**\n"
            f"Rename this store's fingerprint files to **{number}.xlsx** (or .csv/.xls) before uploading.",
        )
        if not weekend_days:
            _flash("info", "No weekend days selected → this store is treated as ROTATIONAL (1 day off per week).")
        _flash("caption", "The change takes effect in the report generator after the next app restart/redeploy.")
        if editing_name is None:
            # New widget keys -> the next store starts from a blank form.
            st.session_state["sm_form_gen"] = st.session_state.get("sm_form_gen", 0) + 1
        st.rerun()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    if editable_names:
        st.subheader("🗑️ Delete a store added here")
        st.caption("Built-in stores can only be changed by the administrator in config.py.")
        del_name = st.selectbox("Store to delete:", editable_names, key=f"sm_del_store_{company}")
        confirm = st.checkbox(
            f"I confirm deleting '{del_name}' from {company}",
            key=f"sm_del_confirm_{company}_{del_name}",
        )
        if st.button("Delete store", disabled=not confirm, key=f"sm_del_btn_{company}"):
            custom.get(company, {}).pop(del_name, None)
            if not custom.get(company):
                custom.pop(company, None)
            pushed, message = _save_custom_stores(custom)
            _flash("success" if pushed else "warning", message)
            _flash("success", f"🗑️ Store '{del_name}' deleted from {company}.")
            st.session_state.pop(f"sm_del_confirm_{company}_{del_name}", None)
            st.rerun()
