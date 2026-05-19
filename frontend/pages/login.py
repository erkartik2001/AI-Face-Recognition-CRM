import streamlit as st

from utils.api_client import APIClient

from utils.auth import (
    save_login,
    is_logged_in,
    logout
)


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Face CRM Login",
    layout="centered"
)


# -----------------------------
# INIT API
# -----------------------------

api = APIClient()


# -----------------------------
# TITLE
# -----------------------------

st.title("AI Face Recognition CRM")


# -----------------------------
# ALREADY LOGGED IN
# -----------------------------

if is_logged_in():

    st.success("Already Logged In")

    if st.button("Logout"):

        logout()

        st.rerun()

    st.stop()


# -----------------------------
# LOGIN FORM
# -----------------------------

with st.form("login_form"):

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    login_button = st.form_submit_button(
        "Login"
    )


# -----------------------------
# LOGIN LOGIC
# -----------------------------

if login_button:

    if not username or not password:

        st.error("Please fill all fields")

    else:

        with st.spinner("Logging In..."):

            response = api.login(
                username,
                password
            )

            st.write(response)


        # SUCCESS
        if response.get("success") or "access_token" in response:

            token = response.get("access_token")

            # user_data = api.get_me("user")
            user_data = api.get_me(token)

            # print("-0-0-0-0-0-0-0-0-0-00-0-0",user_data)


            # Save session
            save_login(
                token,
                user_data
            )


            st.success("Login Successful")

            st.rerun()


        # FAILED
        else:

            st.error(
                response.get(
                    "message",
                    "Login Failed"
                )
            )