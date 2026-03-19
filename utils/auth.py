"""
Sign-in / Sign-up gate (soft gate). Options:
- Continue with Google (OAuth 2.0; GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_OAUTH_REDIRECT_URI).
- Continue with email: name, age, country, email (no password). Stored in data/users.json.

OAuth callback is handled on the main page (app.py) because the redirect URI must match one URL.

OAuth `state` is HMAC-signed with the client secret so we can verify the callback after Google
redirects back — Streamlit often does not keep session_state across that round trip.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st

USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"

GOOGLE_OAUTH_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def _secrets_or_env(key: str, default: str = "") -> str:
    try:
        v = st.secrets.get(key, default)
        if v is not None and str(v).strip():
            return str(v).strip()
    except Exception:
        pass
    return os.environ.get(key, default).strip()


def get_google_oauth_config():
    """
    Returns (client_id, client_secret, redirect_uri) or None if not fully configured.
    redirect_uri must match Google Cloud Console exactly (including trailing slash).
    """
    client_id = _secrets_or_env("GOOGLE_CLIENT_ID")
    client_secret = _secrets_or_env("GOOGLE_CLIENT_SECRET")
    redirect_uri = _secrets_or_env("GOOGLE_OAUTH_REDIRECT_URI")
    if not client_id or not client_secret or not redirect_uri:
        return None
    return (client_id, client_secret, redirect_uri)


def _client_config_web(client_id: str, client_secret: str, redirect_uri: str) -> dict:
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }


def _qp_first(key: str) -> str | None:
    """Get a single query param value (Streamlit may return str or sequence)."""
    try:
        v = st.query_params.get(key)
    except Exception:
        return None
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else None
    return str(v) if v else None


def _clear_oauth_query_params():
    for key in ("code", "state", "scope", "error", "error_description"):
        try:
            if key in st.query_params:
                del st.query_params[key]
        except Exception:
            pass


def _make_signed_oauth_state(client_secret: str) -> str:
    """Random nonce + HMAC so callback can be verified without Streamlit session_state."""
    nonce = secrets.token_urlsafe(24)
    sig = hmac.new(
        client_secret.encode("utf-8"),
        nonce.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")
    return f"{nonce}.{sig_b64}"


def _verify_signed_oauth_state(state_q: str, client_secret: str) -> bool:
    if not state_q or "." not in state_q:
        return False
    nonce, sig_b64 = state_q.rsplit(".", 1)
    if not nonce or not sig_b64:
        return False
    expected = hmac.new(
        client_secret.encode("utf-8"),
        nonce.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected_b64 = base64.urlsafe_b64encode(expected).decode("ascii").rstrip("=")
    return hmac.compare_digest(sig_b64, expected_b64)


def _fetch_userinfo(access_token: str) -> dict:
    req = urllib.request.Request(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return {}


def handle_google_oauth_callback() -> bool:
    """
    Run on app.py every load. If URL has OAuth callback params, process and return True
    (caller should st.stop() so the rest of the home page does not render).
    """
    cfg = get_google_oauth_config()
    if not cfg:
        return False

    err = _qp_first("error")
    if err:
        st.error(f"Google sign-in was cancelled or failed ({err}).")
        _clear_oauth_query_params()
        return True

    code = _qp_first("code")
    if not code:
        return False

    try:
        from google_auth_oauthlib.flow import Flow
    except ImportError:
        st.error("Missing package: install `google-auth-oauthlib` (see requirements.txt).")
        _clear_oauth_query_params()
        return True

    _, _, redirect_uri = cfg
    state_q = _qp_first("state") or ""
    cid, csec, _ = cfg
    if not _verify_signed_oauth_state(state_q, csec):
        st.error(
            "Sign-in couldn’t complete (invalid or expired link). "
            "Open **Upload & Clean** and click **Sign in with Google** again."
        )
        _clear_oauth_query_params()
        return True

    try:
        flow = Flow.from_client_config(
            _client_config_web(cid, csec, redirect_uri),
            scopes=GOOGLE_OAUTH_SCOPES,
            redirect_uri=redirect_uri,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        token = getattr(creds, "token", None)
        if not token:
            raise ValueError("No access token from Google")
        info = _fetch_userinfo(token)
        email = (info.get("email") or "").strip()
        name = (info.get("name") or "").strip()
        if not email:
            st.error("Google did not return an email. Try another account or use **Continue with email**.")
            _clear_oauth_query_params()
            return True
        st.session_state.logged_in = True
        st.session_state.user_email = email
        if name:
            st.session_state.user_name_google = name
        _clear_oauth_query_params()
        st.switch_page("pages/1_Upload_and_Clean.py")
    except Exception as exc:
        st.error(f"Sign-in failed: {exc}")
        _clear_oauth_query_params()
    return True


def _google_authorization_url() -> str | None:
    cfg = get_google_oauth_config()
    if not cfg:
        return None
    try:
        from google_auth_oauthlib.flow import Flow
    except ImportError:
        return None
    cid, csec, redirect_uri = cfg
    state = _make_signed_oauth_state(csec)
    flow = Flow.from_client_config(
        _client_config_web(cid, csec, redirect_uri),
        scopes=GOOGLE_OAUTH_SCOPES,
        redirect_uri=redirect_uri,
    )
    authorization_url, _ = flow.authorization_url(
        access_type="online",
        include_granted_scopes="true",
        state=state,
        prompt="select_account",
    )
    return authorization_url


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
        auth_url = _google_authorization_url()
        if auth_url:
            cfg = get_google_oauth_config()
            redirect_exact = cfg[2] if cfg else ""
            st.markdown(
                "Sign in with your Google account. You’ll return here after Google confirms your email."
            )
            st.link_button("Sign in with Google", auth_url, use_container_width=True, type="primary")
            st.caption(
                "If Google says the app doesn’t comply with OAuth policy, the **redirect URI** is missing or wrong "
                "for this Client ID — fix it in Google Cloud (see below)."
            )
            with st.expander("Google Cloud: register this redirect URI (required)"):
                st.markdown(
                    "1. Open [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Credentials**.\n"
                    "2. Click your **OAuth 2.0 Client ID** (the same one as `GOOGLE_CLIENT_ID` in Streamlit secrets).\n"
                    "3. Under **Authorized redirect URIs**, click **+ ADD URI**.\n"
                    "4. Paste **exactly** this (copy from the box — trailing `/` matters):"
                )
                st.code(redirect_exact or _secrets_or_env("GOOGLE_OAUTH_REDIRECT_URI"), language=None)
                st.markdown(
                    "5. Under **Authorized JavaScript origins**, add the same host **without** path, e.g. "
                    "`https://messclean-bhaskar.streamlit.app` (no trailing slash).\n"
                    "6. **Save**. Wait 1–2 minutes, then try again.\n\n"
                    "**Tip:** Add **both** `https://…streamlit.app` and `https://…streamlit.app/` if unsure which Google expects."
                )
        else:
            st.info(
                "Add **GOOGLE_CLIENT_ID**, **GOOGLE_CLIENT_SECRET**, and **GOOGLE_OAUTH_REDIRECT_URI** "
                "to Streamlit secrets (or environment variables) to enable Google sign-in."
            )

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
