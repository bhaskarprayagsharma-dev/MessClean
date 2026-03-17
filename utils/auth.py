"""
Sign-in / Sign-up gate (soft gate). Options:
- Continue with Google (OAuth; requires GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, redirect URI).
- Continue with email: name, age, country, email (no password). Stored in data/users.json.
Sets st.session_state.logged_in = True and optionally user info.
"""
import streamlit as st
import json
import os
from pathlib import Path

USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"


def _ensure_data_dir():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_users():
    _ensure_data_dir()
    if not USERS_FILE.exists():
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_user(name: str, age: str, country: str, email: str):
    _ensure_data_dir()
    users = _load_users()
    users.append({
        "name": name,
        "age": str(age),
        "country": country,
        "email": email,
    })
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def render_login_gate():
    """
    If st.session_state.logged_in is True, return True (user can proceed).
    Otherwise render the sign-in/sign-up form and return False.
    """
    if st.session_state.get("logged_in"):
        return True

    st.subheader("Create a free MessClean profile to keep improving your Excel cleaning results")
    st.caption("We ask for your role and country so we can prioritize the right features.")

    tab1, tab2 = st.tabs(["Continue with Google", "Continue with email"])

    with tab1:
        st.markdown("""
        **Google sign-in** will be available once you configure OAuth.

        To enable:
        1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
        2. Enable the Google+ API (or Google Identity).
        3. Create OAuth 2.0 credentials (Web application).
        4. Add authorized redirect URI: `https://your-app-url/` (or Streamlit Cloud URL).
        5. Set env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.
        """)
        # Placeholder: when OAuth is implemented, check env and show "Sign in with Google" button
        google_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        if google_id:
            if st.button("Sign in with Google", key="google_signin"):
                st.info("OAuth flow not yet implemented. Use 'Continue with email' for now.")
        else:
            st.caption("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to enable.")

    with tab2:
        with st.form("email_signup"):
            name = st.text_input("Name (optional)", key="auth_name")
            age = st.text_input("Age (optional)", key="auth_age")
            country = st.text_input("Country (required)", key="auth_country")
            email = st.text_input("Email (required)", key="auth_email")
            submitted = st.form_submit_button("Continue")
            if submitted:
                if not country or not country.strip():
                    st.error("Country is required.")
                elif not email or not email.strip():
                    st.error("Email is required.")
                else:
                    _save_user(
                        name or "",
                        age or "",
                        country.strip(),
                        email.strip(),
                    )
                    st.session_state.logged_in = True
                    st.session_state.user_email = email.strip()
                    st.success("You're in! You can now use Upload & Clean.")
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()

    return False
