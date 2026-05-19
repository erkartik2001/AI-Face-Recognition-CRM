import streamlit as st

from utils.auth import (
    is_logged_in,
    get_token,
    get_user
)

from utils.api_client import APIClient


# -----------------------------
# AUTH
# -----------------------------

if not is_logged_in():

    st.warning("Login First")

    st.stop()


user = get_user()

if user["role"] != "admin":

    st.error("Admin Only")

    st.stop()


# -----------------------------
# INIT
# -----------------------------

api = APIClient()

token = get_token()


# -----------------------------
# PAGE
# -----------------------------

st.title("Change User Password")


with st.form("change_password_form"):

    username = st.text_input(
        "Username"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    submit = st.form_submit_button(
        "Change Password"
    )


# -----------------------------
# CHANGE PASSWORD
# -----------------------------

if submit:

    response = api.change_password(
        username,
        new_password,
        token
    )

    if response.get("success"):

        st.success("Password Changed")

    else:

        st.error(
            response.get(
                "message",
                "Failed"
            )
        )