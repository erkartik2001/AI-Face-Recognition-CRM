# Verify login

import json


USERS_FILE = "backend/users.json"


class AuthService:

    def load_users(self):

        with open(USERS_FILE, "r") as f:
            return json.load(f)

    def save_users(self, users):

        with open(USERS_FILE, "w") as f:

            json.dump(
                users,
                f,
                indent=4
            )

    def authenticate(
        self,
        username,
        password
    ):

        users = self.load_users()

        for user in users:

            if (
                user["username"] == username and
                user["password"] == password
            ):

                return user

        return None

    def create_user(
        self,
        username,
        password,
        role="user"
    ):

        users = self.load_users()

        for user in users:

            if user["username"] == username:
                return False

        users.append({
            "username": username,
            "password": password,
            "role": role
        })

        self.save_users(users)

        return True

    def change_password(
        self,
        username,
        new_password
    ):

        users = self.load_users()

        for user in users:

            if user["username"] == username:

                user["password"] = new_password

                break

        self.save_users(users)