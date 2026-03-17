import streamlit as st
import pandas as pd
import os

from modules.sheet_parser import read_excel, ensure_unique_column_names
from modules.pipeline import run_detect_pipeline, run_apply_pipeline
from utils.file_handler import validate_file
from utils.nav import render_top_nav
from utils.auth import render_login_gate
from utils.feedback_to_sheet import render_feedback_form_for_download
from utils.report_builder import build_excel_with_report

# Handle logo link: ?go=home -> switch to app.py
if st.query_params.get("go") == "home":
    st.switch_page("app.py")

# Same page config and CSS as home (sidebar already hidden via CSS)
try:
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

render_top_nav(current="upload")

# Auth gate: must be logged in to use this page
if not render_login_gate():
    st.stop()

st.title("Upload Excel File")

# Session state for caching
def _init_session_state():
    keys = ["cleaned_df", "metadata", "reports", "proposed_changes", "base_df", "upload_session_key"]
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = None if k != "proposed_changes" else []

_init_session_state()

uploaded_file = st.file_uploader(
    "Drag and drop Excel file",
    type=["xlsx", "xls"],
)

if uploaded_file:
    if uploaded_file.size > 50 * 1024 * 1024:
        st.error("File exceeds 50MB limit.")
        st.stop()
    if uploaded_file.size <= 50 * 1024 * 1024:
        st.caption("Files larger than 100,000 rows or 50MB are not supported.")

if uploaded_file:
    valid, msg = validate_file(uploaded_file)
    if not valid:
        st.error(msg)
        st.stop()

    sheets = read_excel(uploaded_file)
    sheet_names = list(sheets.keys())
    selected = st.selectbox("Select sheet", sheet_names)
    df = sheets[selected]

    # Clear cleaning state when file or sheet changes
    current_key = (uploaded_file.name, selected)
    if st.session_state.get("upload_session_key") != current_key:
        st.session_state.upload_session_key = current_key
        st.session_state.base_df = None
        st.session_state.proposed_changes = []
        st.session_state.metadata = None
        st.session_state.cleaned_df = None
        st.session_state.reports = None
        st.session_state.feedback_submitted = False

    # Handle duplicate column names
    df, dup_renames = ensure_unique_column_names(df)
    if dup_renames:
        st.warning(
            "Duplicate column names were renamed: "
            + ", ".join(f"'{a}' → '{b}'" for a, b in dup_renames[:5])
            + (" …" if len(dup_renames) > 5 else "")
        )

    # Empty sheet
    if df.empty:
        st.warning("This sheet is empty. Select another sheet or upload a different file.")
        st.stop()

    st.write("Preview")
    st.dataframe(df.head())

    if st.button("Start Cleaning"):
        with st.spinner("Detecting changes..."):
            metadata, proposed = run_detect_pipeline(df.copy())

        st.session_state.base_df = df.copy()
        st.session_state.proposed_changes = proposed
        st.session_state.metadata = metadata
        st.session_state.cleaned_df = None
        st.session_state.reports = None
        st.session_state.feedback_submitted = False

        if not proposed:
            st.info("No changes detected. Your data looks clean already.")
            cleaned_df, meta, reps = run_apply_pipeline(df.copy(), metadata, [], [])
            st.session_state.cleaned_df = cleaned_df
            st.session_state.metadata = meta
            st.session_state.reports = reps
        else:
            st.success(f"Detected {len(proposed)} proposed change(s). Review and select which to apply.")

    proposed = st.session_state.proposed_changes
    base_df = st.session_state.base_df

    if proposed and base_df is not None:
        st.subheader("Review proposed changes")
        approved_ids = set()

        for i, change in enumerate(proposed):
            cid = change["change_id"]
            tool = change.get("tool", "")
            target_display = change.get("target_display", str(change.get("target", "")))
            before = change.get("before_sample", [])
            after = change.get("after_sample", [])

            checkbox_key = f"approve_{i}_{cid}"

            with st.expander(f"{target_display} ({tool})", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 1])

                with col1:
                    st.markdown("**Before**")
                    st.dataframe(
                        pd.DataFrame({"Value": before}),
                        use_container_width=True,
                        height=min(220, 50 + len(before) * 25),
                    )

                with col2:
                    st.markdown("**After**")
                    if after and not isinstance(after[0], (list, tuple)):
                        after_df = pd.DataFrame({"Value": after})
                    else:
                        after_df = pd.DataFrame(after) if after else pd.DataFrame()
                    st.dataframe(
                        after_df,
                        use_container_width=True,
                        height=min(220, 50 + max(len(after), 1) * 25),
                    )

                with col3:
                    st.markdown("**Apply?**")
                    if st.checkbox("Apply this change", key=checkbox_key, value=True):
                        approved_ids.add(cid)

        if st.button("Apply selected changes"):
            with st.spinner("Applying changes..."):
                cleaned_df, metadata, reports = run_apply_pipeline(
                    base_df.copy(),
                    st.session_state.metadata,
                    approved_ids,
                )

            st.session_state.cleaned_df = cleaned_df
            st.session_state.metadata = metadata
            st.session_state.reports = reports
            st.session_state.feedback_submitted = False
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

    cleaned_df = st.session_state.cleaned_df
    metadata = st.session_state.metadata
    reports = st.session_state.reports

    if cleaned_df is not None and metadata is not None and reports is not None:
        st.success("Cleaning completed")
        st.write("Preview cleaned data")
        st.dataframe(cleaned_df.head())
        st.write("Operations performed")
        st.json(metadata)

        # Pay ₹5 or Fill feedback to download (feedback form writes to Google Sheet or local file)
        render_feedback_form_for_download(cleaned_df, metadata, reports)

        if st.button("Start over"):
            st.session_state.cleaned_df = None
            st.session_state.metadata = None
            st.session_state.reports = None
            st.session_state.base_df = None
            st.session_state.proposed_changes = []
            st.session_state.feedback_submitted = False
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
