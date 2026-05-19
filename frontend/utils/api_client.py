"""
HANDLES:

- Backend API Requests
- JWT Token Headers
- ALL HTTP Communication

"""

import requests


BASE_URL = "http://127.0.0.1:8000"


class APIClient:

    def __init__(self):

        self.base_url = BASE_URL


    # =====================================================
    # AUTH APIs
    # =====================================================

    def login(
        self,
        username,
        password
    ):

        url = f"{self.base_url}/login"

        payload = {

            "username": username,
            "password": password

        }

        response = requests.post(
            url,
            json=payload
        )

        return response.json()


    def create_user(
        self,
        username,
        password,
        role,
        token
    ):

        url = f"{self.base_url}/create-user"

        headers = {

            "Authorization": f"Bearer {token}"

        }

        payload = {

            "username": username,
            "password": password,
            "role": role

        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        return response.json()


    def change_password(
        self,
        username,
        new_password,
        token
    ):

        url = f"{self.base_url}/change-password"

        headers = {

            "Authorization": f"Bearer {token}"

        }

        payload = {
            "username" : username,
            "new_password": new_password

        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        return response.json()


    def get_me(
        self,
        token
    ):

        url = f"{self.base_url}/me"

        headers = {

            "Authorization": f"Bearer {token}"

        }

        response = requests.get(
            url,
            headers=headers
        )

        return response.json()


    # =====================================================
    # FACE SEARCH APIs
    # =====================================================

    def search_face(
        self,
        image_file,
        token
    ):

        url = f"{self.base_url}/search-face"

        headers = {

            "Authorization": f"Bearer {token}"

        }

        files = {

            "file": image_file

        }

        response = requests.post(
            url,
            headers=headers,
            files=files
        )

        return response.json()


    # =====================================================
    # FACE UPLOAD APIs
    # =====================================================

    def upload_face(
        self,
        image_file,
        token
    ):

        url = f"{self.base_url}/upload-face"

        headers = {

            "Authorization": f"Bearer {token}"

        }

        files = {

            "file": image_file

        }

        response = requests.post(
            url,
            headers=headers,
            files=files
        )

        return response.json()


    # =====================================================
    # INDEXING APIs
    # =====================================================

    def start_indexing(
        self,
        count,
        token
    ):

        url = f"{self.base_url}/start-indexing"

        headers = {

            "Authorization": f"Bearer {token}"

        }

        payload = {

            "count": count

        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        return response.json()


    # =====================================================
    # HOME API
    # =====================================================

    def home(self):

        url = f"{self.base_url}/"

        response = requests.get(url)

        return response.json()