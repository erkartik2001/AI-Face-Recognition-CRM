import streamlit as st

from utils.auth import (
    is_logged_in,
    get_user,
    logout
)


# -----------------------------
# AUTH CHECK
# -----------------------------

if not is_logged_in():

    st.warning("Please login first")

    st.stop()


# -----------------------------
# GET USER
# -----------------------------

user = get_user()


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)


# -----------------------------
# TITLE
# -----------------------------

st.title("AI Face Recognition CRM")


# -----------------------------
# USER INFO
# -----------------------------

st.success(
    f"Logged in as: {user['username']}"
    # f"Logged in as: {user}"
)

st.write(
    f"Role: {user['role']}"
)


# -----------------------------
# QUICK ACTIONS
# -----------------------------

st.subheader("Quick Actions")


col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "Search Faces",
        use_container_width=True
    ):

        st.switch_page(
            "pages/search_face.py"
        )


with col2:

    if st.button(
        "Create User",
        use_container_width=True
    ):

        st.switch_page(
            "pages/create_user.py"
        )


with col3:

    if st.button(
        "Index Images",
        use_container_width=True
    ):

        st.switch_page(
            "pages/indexing.py"
        )


# -----------------------------
# LOGOUT
# -----------------------------

st.divider()

if st.button("Logout"):

    logout()

    st.rerun()