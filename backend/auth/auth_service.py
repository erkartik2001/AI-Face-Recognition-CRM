# Verify login

import json

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


USERS_FILE = "backend/users.json"


class AuthService:

    def __init__(self):

        with open(USERS_FILE, "r") as f:
            self.users = json.load(f)

    def authenticate_user(
        self,
        username,
        password
    ):

        for user in self.users:

            if user["username"] == username:

                valid = pwd_context.verify(
                    password,
                    user["password"]
                )

                if valid:
                    return user

        return None