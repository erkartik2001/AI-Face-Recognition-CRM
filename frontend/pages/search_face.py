# import streamlit as st

# from utils.auth import (
#     is_logged_in,
#     get_token
# )

# from utils.api_client import APIClient

# from PIL import ImageFile

# ImageFile.LOAD_TRUNCATED_IMAGES = True


# # -----------------------------
# # AUTH
# # -----------------------------

# if not is_logged_in():

#     st.warning("Login First")

#     st.stop()


# # -----------------------------
# # INIT
# # -----------------------------

# api = APIClient()

# token = get_token()


# # -----------------------------
# # PAGE
# # -----------------------------

# st.title("Search Face")


# uploaded_file = st.file_uploader(
#     "Upload Face Image",
#     type=["jpg", "jpeg", "png"]
# )


# # -----------------------------
# # SEARCH
# # -----------------------------

# if uploaded_file:

#     st.image(
#         uploaded_file,
#         caption="Uploaded Image",
#         width=300
#     )

#     if st.button("Search Face"):

#         with st.spinner("Searching..."):

#             results = api.search_face(
#                 uploaded_file,
#                 token
#             )


#         # DEBUG
#         st.write(results)


#         if not results:

#             st.error("No Match Found")


#         else:

#             st.success(
#                 f"Matches Found: {len(results)}"
#             )

#             for result in results:

#                 st.divider()

#                 st.image(
#                     result["file_url"],
#                     width=250
#                 )

#                 st.write(
#                     f"Similarity: {result['similarity']:.4f}"
#                 )

#                 st.write(
#                     result["file_name"]
#                 )

import streamlit as st

from utils.auth import (
    is_logged_in,
    get_token
)

from utils.api_client import APIClient

from PIL import ImageFile

import requests

from PIL import Image

from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True


# -----------------------------
# AUTH CHECK
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
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Search Face",
    layout="wide"
)


# -----------------------------
# TITLE
# -----------------------------

st.title("Search Face")


# -----------------------------
# FILE UPLOAD
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload Face Image",
    type=["jpg", "jpeg", "png"]
)


# -----------------------------
# SEARCH FLOW
# -----------------------------

if uploaded_file:

    st.image(
        uploaded_file,
        caption="Uploaded Image",
        width=300
    )

    if st.button(
        "Search Face",
        use_container_width=True
    ):

        with st.spinner("Searching Face..."):

            response = api.search_face(
                uploaded_file,
                token
            )


        # DEBUG RESPONSE
        # st.write(response)


        matches = response.get(
            "matches",
            []
        )


        # -----------------------------
        # NO MATCH
        # -----------------------------

        if len(matches) == 0:

            st.error("No Match Found")


        # -----------------------------
        # MATCH FOUND
        # -----------------------------

        else:

            result = matches[0]

            st.success("Match Found")

            st.write(
                f"Similarity Score: {result['similarity']:.4f}"
            )

            st.write(
                f"File Name: {result['file_name']}"
            )



            try:

                # st.image(
                #     result["file_url"],
                #     caption="Matched Face",
                #     width=350
                # )

                response = requests.get(
                    result["file_url"]
                )

                img = Image.open(
                    BytesIO(response.content)
                )

                st.image(
                    img,
                    caption="Matched Face",
                    width=350
                )



            except Exception:

                st.warning(
                    "Image Preview Not available"
                )


            # st.write(
            #     f"Similarity Score: {result['similarity']:.4f}"
            # )

            # st.write(
            #     f"File Name: {result['file_name']}"
            # )

        if len(matches) != 0:
            st.link_button(
                "Open Original Image",
                result["file_url"]
            )