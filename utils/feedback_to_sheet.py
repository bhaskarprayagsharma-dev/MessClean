"""
Feedback form for "Fill feedback to download". Required: occupation, country, multi-select upgrades.
Optional: free text, name. On submit: append row to Google Sheet (if configured), then return True
so the download button can be shown.

Setup (document in README):
- Create a Google Sheet. Share it with the service account email (if using service account).
- Recommended (Streamlit Cloud): set secret GOOGLE_SERVICE_ACCOUNT_JSON to the JSON contents (triple-quoted).
- Alternative: set env GOOGLE_SHEETS_CREDENTIALS_JSON to a service account JSON file path (local dev).
- Set secret or env FEEDBACK_SHEET_ID to override; otherwise the default MessClean Feedback sheet is used.
- pip install gspread google-auth.
"""
import os
import streamlit as st
from pathlib import Path
import json

# Optional: store feedback locally if Google Sheet not configured
FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.json"

# Default MessClean Feedback sheet (used when FEEDBACK_SHEET_ID is not in secrets/env)
FEEDBACK_SHEET_ID_DEFAULT = "10RTSuq4RGVy0CBN3Fmxi2gzUqafalJrvkfH7NdbyiMI"


def _ensure_data_dir():
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)


def _append_feedback_local(data: dict):
    _ensure_data_dir()
    import json
    rows = []
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                rows = json.load(f)
        except Exception:
            rows = []
    rows.append(data)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def append_feedback_to_sheet(
    free_text: str,
    name: str,
    occupation: str,
    country: str,
    upgrades: list,
) -> tuple[bool, str]:
    """
    Append one feedback row to Google Sheet (or local file if not configured).
    Returns (success, error_message).
    """
    row = {
        "free_text": free_text,
        "name": name,
        "occupation": occupation,
        "country": country,
        "upgrades": ",".join(upgrades) if upgrades else "",
    }

    # Prefer Streamlit secrets (works on Streamlit Cloud)
    sheet_id = ""
    service_account_json = ""
    try:
        sheet_id = str(st.secrets.get("FEEDBACK_SHEET_ID", "")).strip()
        service_account_json = str(st.secrets.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")).strip()
    except Exception:
        pass

    # Fall back to env vars (useful for local dev), then to default MessClean sheet
    if not sheet_id:
        sheet_id = os.environ.get("FEEDBACK_SHEET_ID", "").strip()
    if not sheet_id:
        sheet_id = FEEDBACK_SHEET_ID_DEFAULT
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON", "").strip()

    if sheet_id and service_account_json:
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            info = json.loads(service_account_json)
            creds = Credentials.from_service_account_info(info, scopes=scopes)
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(sheet_id)
            # Use first worksheet
            ws = sh.sheet1
            ws.append_row([row.get("name", ""), row.get("occupation", ""), row.get("country", ""), row.get("upgrades", ""), row.get("free_text", "")])
            return True, ""
        except Exception as e:
            _append_feedback_local(row)
            return True, ""  # still succeed so user can download; data is in local file
    elif sheet_id and creds_path and os.path.isfile(creds_path):
        # Local dev fallback: use a JSON file path from env
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(sheet_id)
            ws = sh.sheet1
            ws.append_row([row.get("name", ""), row.get("occupation", ""), row.get("country", ""), row.get("upgrades", ""), row.get("free_text", "")])
            return True, ""
        except Exception:
            _append_feedback_local(row)
            return True, ""
    else:
        _append_feedback_local(row)
        return True, ""


UPGRADE_OPTIONS = [
    "More cleaning tools",
    "API access",
    "Batch upload (multiple files)",
    "Custom rules",
    "Export to other formats",
    "Priority support",
]


def render_feedback_form_for_download(cleaned_df, metadata, reports, file_name: str = "cleaned_data.xlsx"):
    """
    Render "Fill feedback to download (free)" or "Support us with ₹5". When feedback form
    is submitted with required fields, append to Google Sheet (or local file), then show
    the download button.
    """
    st.markdown("**Early access:** help us improve by sharing feedback or tipping ₹5.")
    st.markdown("**To download:** choose one option below.")

    option = st.radio(
        "Choose one",
        ["Fill feedback to download (free for early users)", "Or support us with ₹5"],
        label_visibility="collapsed",
        key="download_option",
    )

    if "₹5" in option:
        if st.button("Proceed to payment (Razorpay)", key="pay_razorpay"):
            st.info("Razorpay integration pending. Use 'Fill feedback to download' for now.")
        return

    # Fill feedback to download
    st.markdown("Complete the form below (required fields) and click **Submit & Download**.")

    with st.form("feedback_for_download"):
        name = st.text_input("Name (optional)", key="fb_name")
        occupation = st.text_input("What do you do? (required)", key="fb_occupation")
        country = st.text_input("Where are you based? (required)", key="fb_country")
        upgrades = st.multiselect(
            "Which upgrades would you like to see?",
            UPGRADE_OPTIONS,
            key="fb_upgrades",
        )
        free_text = st.text_area("Anything else? (optional)", key="fb_free")
        submitted = st.form_submit_button("Submit & Download")

    if submitted:
        if not occupation or not occupation.strip():
            st.error("What do you do? is required.")
        elif not country or not country.strip():
            st.error("Where are you based? is required.")
        else:
            success, err = append_feedback_to_sheet(
                free_text or "",
                name or "",
                occupation.strip(),
                country.strip(),
                upgrades or [],
            )
            if success:
                st.session_state.feedback_submitted = True
                st.success("You've just helped shape MessClean. Your download is ready below.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

    # Show download button if feedback was just submitted (on rerun)
    if st.session_state.get("feedback_submitted"):
        from utils.report_builder import build_excel_with_report
        st.markdown("✓ **You've just helped shape MessClean.**")
        excel_bytes = build_excel_with_report(cleaned_df, metadata, reports)
        st.download_button(
            "Download Cleaned Excel",
            excel_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_after_feedback",
        )
