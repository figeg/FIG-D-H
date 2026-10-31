# D&H Group Web App (FIG-D-H)

A web application for the D&H Group team that turns raw fingerprint (punch) machine files into ready-to-share Excel attendance reports. It automatically handles vacations, sick leave, days off, public holidays, and store schedules — so you don't have to calculate anything by hand.

You use it from your web browser. No technical knowledge is needed.

---

## 🧭 What's Inside the App

After logging in, the sidebar on the left has these pages:

| Page | What it does |
|------|--------------|
| 🏠 **Home** | Welcome screen |
| ⏰ **Fingerprint Reports** | The main tool — builds the employee attendance report (see guide below) |
| 🏪 **Add New Store** | Register a new store yourself — no developer needed (see below) |
| 🔍 **Diagnostics** | For checking a specific employee's data when something looks wrong |

---

## 🚀 How to Use the Fingerprint Reports Page (Step by Step)

1. **Log in** with the username and password provided by your administrator.
2. In the sidebar, click **⏰ Fingerprint Reports**.
3. **Select the company** from the dropdown: *Al-hadabah times*, *D&H*, *D&co*, *D&CO Jordan*, or *Second Cup*.
   ⚠️ Make sure the company matches the files you are about to upload — each company has its own date formats and rules.
4. **Upload the fingerprint files** (.csv, .xls, or .xlsx) exported from the punch machines. You can upload several files at once.
5. *(Optional)* **Upload the Vacation/Sick/Emergency adjustments file** if you have one for this period.
6. **Type a filename** for the report (or keep the default).
7. Click **🚀 Generate Reports** and wait a moment while it processes.
8. Review the results on screen, then click the **download button** to save the Excel report.
9. Starting over with new files? Click **🔄 New Files (Clear and Reset)** first.

### 📥 What the downloaded Excel report contains

- **Detailed Daily Report** — every employee, every day, with punch times and shift durations
- **Summary** — one row per employee: present days, absent days, total hours, single-punch days, etc.
- **Adjusted Absences (Per Type)** — absences broken down by reason (vacation, sick, etc.)
- **Pending OFF Credits** — pending off days owed/used
- **Error Log** — anything the app could not read, so you can fix and re-upload
- **Days_Flags** — day-by-day status flags used in the calculations

### 📅 Store schedule codes (from Google Sheets)

The app reads each store's schedule directly from its Google Sheet and compares it with the actual punches. Use these codes in the sheets:

| Code | Meaning | Counted as |
|------|---------|-----------|
| `PT` | Present / working day | Expected to punch |
| `AB` | Absent | **Not** excused |
| `OFF` / `OF` | Off day | Excused |
| `OH` | Half day off | Excused |
| `VC` | Vacation | Excused |
| `SL` | Sick leave | Excused |
| `DP` or `PH` | Public holiday (both codes work) | Excused |
| `XO` | Extra off | Excused |
| `TR` | Transferred | Excused |
| `HD` / `FD` | Half/Full day pending off | Excused (pending logic) |

Small typos in capitalization or extra spaces (e.g. ` ph `) are handled automatically. Any **other** code is ignored by the calculations — stick to this list.

---

## 🏪 How to Use the "Add New Store" Page (Step by Step)

When a new store opens, you can register it yourself — no developer needed. In the sidebar, click **🏪 Add New Store**.

### Adding a store

1. **Select the company** the store belongs to.
2. Under *"What do you want to do?"*, keep **Add a new store** selected.
3. Type the **store name** — write it the way the team knows the store.
4. Pick the **date format** the store's fingerprint machine uses in its export files. Not sure? Open one of its files and look at a date: `25/06/2026` = Day/Month/Year, `06/25/2026` = Month/Day/Year.
5. Pick the **working hours**: 8 or 9 for regular stores; for Second Cup you can also choose 12 or 24 opening hours (24 turns on the round-the-clock shift logic).
6. Check the store's **weekend days** (Mon–Sun checkboxes). If the staff don't have fixed weekends, leave all boxes **unchecked** — the store is then treated as *rotational* (1 day off per week).
7. *(Optional but recommended)* paste the store's **Google Sheet schedule link**. Without it, the store is left out of the Store Ops schedule checks.
8. Click **💾 Save store**.

### 🔢 The store number

After saving, the app shows the store's **number** — for example **141**. This is important: **rename that store's fingerprint files to this number** (`141.xlsx`, `141.csv`…) before uploading them, exactly like the existing stores. The first digit is the company (1 = D&H, 2 = D&co, 3 = Second Cup, 4 = Al-hadabah times, 5 = D&CO Jordan) and the rest is the store's own code — the app picks the next free one automatically. Store names must be unique across all companies (the page will tell you if a name is already taken — e.g. add "Jordan" to the name).

⏳ The new store becomes usable in the Fingerprint Reports page after the app refreshes itself (about 1–2 minutes on the live app).

### Updating or deleting a store

On the same page, choose **Update an existing store** to change a store's date format, hours, weekends, or sheet link — its number never changes. To remove a store, use the **🗑️ Delete** section at the bottom: pick the store, tick the confirmation box, then click Delete.

Only stores that were **added through this page** can be updated or deleted here. The original stores built into the app are listed for reference (open *"📋 Existing stores"* to see every store and its file number) but can only be changed by the administrator.

---

## 📅 Date Formats Are Handled Automatically

Sometimes the fingerprint machine's export switches between day/month/year and month/day/year. You don't need to fix this yourself: the app **detects the actual date format of each file automatically** and adapts, so the report is always generated — nothing is blocked or left out.

When a file's format doesn't match what's configured for that store, you'll see a **yellow "Date format notice"** above the results after generation. The report is still correct and complete; the notice just tells you which file differed, so the administrator can update `config.py` if the machine's format changed permanently.

---

## 🏗️ Infrastructure (Technical Overview)

For administrators and developers:

- **Framework:** [Streamlit](https://streamlit.io) — the whole app is a Python web app; the browser interface, uploads, and downloads are all Streamlit. There is no separate database: everything is processed in memory per session.
- **Hosting & deployment (important):** the live app runs on **Streamlit Community Cloud, which reads the code directly from this GitHub repository**. The app the team uses in the browser is whatever is on the connected branch of the repo — so **pushing a commit to GitHub is what updates the live app** (it redeploys automatically within a minute or two). Nothing is deployed manually. This also means: work in progress should not be pushed to the connected branch, and `requirements.txt` must stay accurate because Streamlit Cloud installs the app's packages from it on every deploy. Official guide: [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) (see also the [Community Cloud overview](https://docs.streamlit.io/deploy/streamlit-community-cloud)).
- **Data processing:** pandas throughout. Excel files are read with openpyxl/xlrd and the final report is written with xlsxwriter.
- **Google Sheets integration:** store operations schedules are fetched live over HTTPS as CSV exports of each store's Google Sheet (no Google account/API key needed — the sheets are read via their share links defined in `config.py` → `STORE_OPS_LINKS`).
- **Configuration:** `config.py` holds the built-in configuration — companies, store codes, per-location date formats, weekend rules, and the Google Sheets links (`COMPANY_CONFIGS`, `LOCATION_MAP`, `STORE_OPS_LINKS`).
- **Custom stores (Add New Store page):** stores added through the app are saved in `custom_stores.json` and merged over `config.py` at startup. The page **auto-commits that file to GitHub** using a token read from Streamlit secrets (`GITHUB_TOKEN` — a fine-grained personal access token limited to this repo with *Contents: read & write*). That commit triggers the normal Streamlit Cloud redeploy, which is how new stores both persist and go live. Without the token, saves are local-only and are lost when Streamlit Cloud restarts — the page warns the user when that's the case.

### Module map

| File | Purpose |
|------|---------|
| `main.py` | App entry point: login, sidebar navigation, page routing |
| `login_page.py` | Login screen |
| `app_ui.py` | Fingerprint Reports page UI (uploads, buttons, results display) |
| `config.py` | All company/store configuration and Google Sheets links |
| `data_processing.py` | Reads and cleans the raw fingerprint files |
| `second_cup_logic.py` | Punch pairing and 24-hour shift logic (repairs faulty punch statuses) |
| `vacation_adjustment.py` | Applies the vacation/sick/emergency adjustments file |
| `pending_offs.py` | Pending off-day credits logic |
| `store_ops_logic.py` | Fetches Google Sheets schedules and finds discrepancies vs. actual punches |
| `report_generation.py` | Builds the summary, reconciles excused absences, exports the Excel file |
| `store_management.py` | The Add New Store page (add/update/delete + GitHub auto-commit) |
| `custom_stores.json` | Stores added through the app (created on first use; merged over config.py) |
| `diagnostics.py` | The Diagnostics page |
| `analysis_functions.py` | Shared attendance calculation helpers |

### Running the app

```bash
# 1. Install Python 3.10+ then, from the project folder:
pip install -r requirements.txt

# 2. Start the app:
streamlit run main.py
```

Streamlit opens the app in your browser at `http://localhost:8501`. This local mode is only for development and testing.

**The team's live version** doesn't need any of this — it is served by Streamlit Community Cloud from the GitHub repo (see *Hosting & deployment* above). To release a change: test it locally, commit, and push to the connected branch on GitHub; Streamlit Cloud picks it up and redeploys automatically.

---

> ⚠️ **Administrators:** everyday store additions now happen through the **Add New Store** page. `config.py` remains the place for advanced rules (employee overrides, alternating weekends, break deductions) and for editing the original built-in stores.
