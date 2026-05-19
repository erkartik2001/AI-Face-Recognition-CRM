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

st.title("Create User")


with st.form("create_user_form"):

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        ["user", "admin"]
    )

    submit = st.form_submit_button(
        "Create User"
    )


# -----------------------------
# CREATE USER
# -----------------------------

if submit:

    response = api.create_user(
        username,
        password,
        role,
        token
    )

    if response.get("success"):

        st.success("User Created")

    else:

        st.error(
            response.get(
                "message",
                "Failed"
            )
        )