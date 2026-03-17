import streamlit as st


def payment_option():
    st.markdown("**To download:** choose one option below to unlock the download button.")
    option = st.radio(
        "Choose one",
        ["Pay ₹5", "Answer survey"],
        label_visibility="collapsed",
    )
    return option
