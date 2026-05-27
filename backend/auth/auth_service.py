# Verify login — PostgreSQL-backed

import pyotp

from passlib.context import CryptContext
from datetime import datetime

from backend.database import SessionLocal
from backend.models import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class AuthService:

    def _get_db(self):
        """Create a new database session."""
        return SessionLocal()

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

    # =========================================
    # AUTHENTICATE
    # =========================================

    def authenticate(
        self,
        username,
        password
    ):

        db = self._get_db()

        try:
            user = db.query(User).filter(
                User.username == username
            ).first()

            if not user:
                return None

            print("CHECKING USER")
            print("USERNAME MATCHED")

            valid = pwd_context.verify(
                password,
                user.password
            )

            print("PASSWORD VALID:", valid)

            if valid:
                return user.to_dict()

            return None

        finally:
            db.close()

    # =========================================
    # CREATE USER
    # =========================================

    def create_user(
        self,
        username,
        password,
        role="user"
    ):

        db = self._get_db()

        try:
            existing = db.query(User).filter(
                User.username == username
            ).first()

            if existing:
                return False

            hashed_password = self.hash_password(
                password
            )

            totp_secret = pyotp.random_base32()

            user = User(
                username=username,
                password=hashed_password,
                role=role,
                totp_secret=totp_secret,
                created_at=datetime.now(),
                last_login=None
            )

            db.add(user)
            db.commit()

            return totp_secret

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    # =========================================
    # VERIFY OTP
    # =========================================

    def verify_otp(
        self,
        username,
        otp
    ):

        db = self._get_db()

        try:
            user = db.query(User).filter(
                User.username == username
            ).first()

            if not user:
                return False

            totp = pyotp.TOTP(user.totp_secret)

            if totp.verify(otp):
                user.last_login = datetime.now()
                db.commit()
                return True

            return False

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    # =========================================
    # CHANGE PASSWORD
    # =========================================

    def change_password(
        self,
        username,
        new_password
    ):

        db = self._get_db()

        try:
            user = db.query(User).filter(
                User.username == username
            ).first()

            if user:
                user.password = self.hash_password(
                    new_password
                )
                db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    # =========================================
    # DELETE USER
    # =========================================

    def delete_user(self, username):

        db = self._get_db()

        try:
            user = db.query(User).filter(
                User.username == username
            ).first()

            if not user:
                return False

            db.delete(user)
            db.commit()

            return True

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    # =========================================
    # GET USER COUNT
    # =========================================

    def get_user_count(self):

        db = self._get_db()

        try:
            return db.query(User).count()

        finally:
            db.close()

    # =========================================
    # LOAD USERS (for backwards compatibility)
    # =========================================

    def load_users(self):
        """Return all users as list of dicts (old JSON format)."""

        db = self._get_db()

        try:
            users = db.query(User).all()
            return [u.to_dict() for u in users]

        finally:
            db.close()

    # =========================================
    # GET USER BY USERNAME
    # =========================================

    def get_user(self, username):
        """Get a single user by username."""

        db = self._get_db()

        try:
            user = db.query(User).filter(
                User.username == username
            ).first()

            if user:
                return user.to_dict()

            return None

        finally:
            db.close()