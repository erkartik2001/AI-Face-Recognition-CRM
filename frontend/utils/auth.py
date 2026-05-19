import streamlit as st


# -----------------------------
# SAVE LOGIN
# -----------------------------

def save_login(
    token,
    user_data
):

    st.session_state["token"] = token

    st.session_state["user"] = user_data

    st.session_state["logged_in"] = True


# -----------------------------
# LOGOUT
# -----------------------------

def logout():

    st.session_state.clear()


# -----------------------------
# CHECK LOGIN
# -----------------------------

def is_logged_in():

    return st.session_state.get(
        "logged_in",
        False
    )


# -----------------------------
# GET TOKEN
# -----------------------------

def get_token():

    return st.session_state.get(
        "token"
    )


# -----------------------------
# GET USER
# -----------------------------

def get_user():

    return st.session_state.get(
        "user"
    )