# Verify login

import json
import os

import pyotp

from passlib.context import CryptContext
from datetime import datetime

USERS_FILE = "backend/users.json"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


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

    # =========================================
    # HASH PASSWORD
    # =========================================

    def hash_password(self, password):

        return pwd_context.hash(password)

    # =========================================
    # VERIFY PASSWORD
    # =========================================

    def verify_password(
        self,
        plain_password,
        hashed_password
    ):

        return pwd_context.verify(
            plain_password,
            hashed_password
        )


    def authenticate(
        self,
        username,
        password
    ):

        users = self.load_users()

        print(users)

        for user in users:

            print("CHECKING USER")

            if user["username"] == username:

                print("USERNAME MATCHED")

                valid = pwd_context.verify(
                    password,
                    user["password"]
                )

                print("PASSWORD VALID:", valid)

                if valid:
                    return user

        return None

    # =========================================
    # CREATE USER
    # =========================================

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

        hashed_password = self.hash_password(
            password
        )

        totp_secret = pyotp.random_base32()

        users.append({

            "username": username,

            "password": hashed_password,

            "role": role,

            "totp_secret": totp_secret,

            "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "last_login" : None
        })

        self.save_users(users)

        return totp_secret

    # =========================================
    # VERIFY OTP
    # =========================================

    def verify_otp(
        self,
        username,
        otp
    ):

        users = self.load_users()

        for user in users:

            if user["username"] == username:

                totp = pyotp.TOTP(
                    user["totp_secret"]
                )

                user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return totp.verify(otp)

        return False

    # =========================================
    # CHANGE PASSWORD
    # =========================================

    def change_password(
        self,
        username,
        new_password
    ):

        users = self.load_users()

        for user in users:

            if user["username"] == username:

                user["password"] = self.hash_password(
                    new_password
                )

                break

        self.save_users(users)