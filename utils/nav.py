"""Shared top navigation bar: Logo as real link (?go=home), then tab-like Upload & Clean."""
import streamlit as st
import os
import base64


def _logo_path():
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
    return path if os.path.isfile(path) else None


def _logo_data_uri():
    path = _logo_path()
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def render_top_nav(current="home"):
    """
    Logo is a single HTML link (?go=home). Upload & Clean is a tab-like button.
    """
    logo_uri = _logo_data_uri()

    col_sp1, col_logo, col_sp2, col_upload, col_sp3 = st.columns([1, 2, 1, 1, 3])

    with col_logo:
        if logo_uri:
            html = f'<a href="?go=home" class="nav-logo-link" title="Home"><img src="{logo_uri}" width="220" style="display:block"/></a>'
            st.markdown(html, unsafe_allow_html=True)
        else:
            if st.button("Home", key="nav_logo_fallback"):
                st.switch_page("app.py")

    with col_upload:
        st.markdown('<div class="nav-tab-btn">', unsafe_allow_html=True)
        if st.button("Upload & Clean", key="nav_upload"):
            st.switch_page("pages/1_Upload_and_Clean.py")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
