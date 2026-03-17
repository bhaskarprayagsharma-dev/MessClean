import streamlit as st

def show_feedback():

    st.subheader("Help Us Improve")

    rating = st.slider("Rate this tool",1,5)

    feedback = st.text_area("What feature should we build next?")

    if st.button("Submit Feedback"):

        st.success("Thank you for your feedback!")
