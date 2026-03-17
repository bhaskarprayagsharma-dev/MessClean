import os
import streamlit as st
from utils.nav import render_top_nav

st.set_page_config(
    page_title="MessClean – Excel Data Cleaner",
    layout="wide",
)


def load_css():
    try:
        with open("assets/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css()

# Inline "Upload & Clean" link: ?navigate=upload -> go to upload page
if st.query_params.get("navigate") == "upload":
    st.switch_page("pages/1_Upload_and_Clean.py")

render_top_nav(current="home")

# Hero section
st.markdown("""
<div class="hero-section">
<h1>Turn messy Excel spreadsheets into clean, trusted data with MessClean.</h1>
<p class="hero-subline">
MessClean is a fast Excel data cleaning tool: upload your spreadsheet, review smart cleaning suggestions, and download a clean workbook. No formulas, no fuss.
</p>
<p class="hero-cta"><a href="?navigate=upload" class="hero-cta-btn">Upload & Clean your first file</a></p>
</div>
""", unsafe_allow_html=True)

# How it works
st.markdown('<h2 class="section-title">How it works</h2>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**1.** Upload your messy Excel sheet.")
with c2:
    st.markdown("**2.** Review suggested changes (with inline previews).")
with c3:
    st.markdown("**3.** Download a clean workbook plus a change report.")

# What MessClean fixes (grid)
st.markdown('<h2 class="section-title">What MessClean fixes in your Excel data</h2>', unsafe_allow_html=True)
FEATURES = [
    ("Mixed quantities", "e.g. 40kg → 40 + unit column", "assets/feature_quantities.png"),
    ("Currency formatting", "₹ $ € normalized", "assets/feature_currency.png"),
    ("Percentage values", "stripped and numeric", "assets/feature_percentage.png"),
    ("Duplicate rows", "removed", "assets/feature_duplicates.png"),
    ("Empty columns", "removed", "assets/feature_empty_columns.png"),
    ("Summary rows", '"Total" / "Subtotal" removable', "assets/feature_summary_rows.png"),
    ("Date inconsistencies", "normalized formats", "assets/feature_dates.png"),
]

# Grid: 3 + 3 + 1 feature cards
row1 = st.columns(3)
row2 = st.columns(3)
for i, (title, desc, img_path) in enumerate(FEATURES):
    if i < 3:
        col = row1[i]
    elif i < 6:
        col = row2[i - 3]
    else:
        col = row2[2]
    with col:
        if os.path.isfile(img_path):
            st.image(img_path, use_container_width=True)
        st.markdown(f"**{title}** — {desc}")
        st.markdown("")

# Trust strip
st.markdown("""
<div class="trust-strip">
<p>Files are processed in memory and deleted at the end of your session. We never share your data.</p>
<p>Built for analysts, operators, and founders who live in Excel.</p>
<p class="trust-help">Need help? <a href="mailto:support@messclean.com">support@messclean.com</a></p>
</div>
""", unsafe_allow_html=True)

# Final CTA (inline link, no separate button)
st.markdown("""
<div class="cta-success">
Click <a href="?navigate=upload" class="cta-inline-link"><strong>Upload & Clean</strong></a> above to start, or use the button in the top bar.
</div>
""", unsafe_allow_html=True)

st.info("Your spreadsheet is processed securely and deleted after the session.")
