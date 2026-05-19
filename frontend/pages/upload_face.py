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

st.title("Upload Face")


uploaded_file = st.file_uploader(
    "Upload New Face",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file:

    st.image(
        uploaded_file,
        width=300
    )

    if st.button("Upload Face"):

        with st.spinner("Uploading..."):

            response = api.upload_face(
                uploaded_file,
                token
            )


        st.success("Upload Complete")

        st.write(response)