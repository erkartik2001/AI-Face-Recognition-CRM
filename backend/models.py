# SQLAlchemy ORM models

from sqlalchemy import (
    Column, Integer, String, Boolean,
    DateTime, Text
)
from sqlalchemy.sql import func

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String(255), unique=True, nullable=False, index=True
    )
    password = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, default="user")
    totp_secret = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        """Return user as dict (matches old JSON format)."""
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "totp_secret": self.totp_secret,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at else None
            ),
            "last_login": (
                self.last_login.strftime("%Y-%m-%d %H:%M:%S")
                if self.last_login else None
            )
        }


class Bucket(Base):
    __tablename__ = "buckets"

    id = Column(Integer, primary_key=True, index=True)
    bucket_name = Column(
        String(255), unique=True, nullable=False, index=True
    )
    is_active = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    created_by = Column(String(255), nullable=True)

    def to_dict(self):
        return {
            "bucket_name": self.bucket_name,
            "is_active": self.is_active,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at else None
            ),
            "created_by": self.created_by
        }


class IndexingState(Base):
    __tablename__ = "indexing_state"

    id = Column(Integer, primary_key=True, index=True)
    bucket_name = Column(
        String(255), unique=True, nullable=False, index=True
    )
    last_indexed = Column(Integer, default=0)
    total_files = Column(Integer, nullable=True)
    last_sync_date = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "last_indexed": self.last_indexed,
            "total_files": self.total_files,
            "last_sync_date": (
                self.last_sync_date.strftime("%Y-%m-%d %H:%M:%S")
                if self.last_sync_date else None
            )
        }
