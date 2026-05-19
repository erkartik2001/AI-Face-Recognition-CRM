import streamlit as st

from utils.auth import (
    is_logged_in,
    get_token
)

from utils.api_client import APIClient


# -----------------------------
# AUTH
# -----------------------------

if not is_logged_in():

    st.warning("Login First")

    st.stop()


# -----------------------------
# INIT
# -----------------------------

api = APIClient()

token = get_token()


# -----------------------------
# PAGE
# -----------------------------

st.title("Index B2 Images")


count = st.number_input(
    "How many images to index?",
    min_value=1,
    max_value=5000,
    value=50
)


if st.button("Start Indexing"):

    with st.spinner("Indexing Images..."):

        response = api.start_indexing(
            count,
            token
        )


    st.success("Indexing Started")

    st.write(response)