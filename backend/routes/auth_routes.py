# Login API

import pyotp
import qrcode
import io
import base64

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel

from backend.auth.auth_service import AuthService

from backend.auth.jwt_handler import create_token

from backend.auth.dependencies import (
    get_current_user
)


router = APIRouter()

auth_service = AuthService()


class LoginRequest(BaseModel):

    username: str
    password: str
    otp: str | None = None


class CreateUserRequest(BaseModel):

    username: str
    password: str
    role: str = "user"


class ChangePasswordRequest(BaseModel):

    username : str
    new_password: str


class DeleteUserRequest(BaseModel):

    username: str



@router.post("/login")
async def login(request: LoginRequest):

    user = auth_service.authenticate(
        request.username,
        request.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # STEP 1:
    # Password correct but OTP not sent yet
    if not request.otp:

        return {
            "success": True,
            "requires_2fa": True
        }

    # STEP 2:
    # Verify OTP
    valid_otp = auth_service.verify_otp(
        request.username,
        request.otp
    )

    if not valid_otp:

        raise HTTPException(
            status_code=401,
            detail="Invalid OTP"
        )

    token = create_token({
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "success": True,
        "access_token": token
    }

@router.post("/create-user")
async def create_user(
    request: CreateUserRequest,
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    totp_secret = auth_service.create_user(
        request.username,
        request.password,
        request.role
    )

    if not totp_secret:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    totp_uri = pyotp.totp.TOTP(
        totp_secret
    ).provisioning_uri(

        name=request.username,

        issuer_name="AI Face CRM"
    )

    qr = qrcode.make(totp_uri)

    buffer = io.BytesIO()

    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode()

    return {

        "success": True,

        "qr_code": qr_base64
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user)
):

    # auth_service.change_password(
    #     current_user["username"],
    #     request.new_password
    # )

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    auth_service.change_password(
        request.username,
        request.new_password
    )

    return {
        "message": "Password updated"
    }


@router.post("/delete-user")
async def delete_user(
    request: DeleteUserRequest,
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    if request.username == current_user["username"]:

        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself"
        )

    result = auth_service.delete_user(
        request.username
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "success": True,
        "message": f"User '{request.username}' deleted"
    }


@router.get("/me")
async def me(
    current_user=Depends(get_current_user)
):

    return current_user

import pyotp


@router.get("/setup-2fa/{username}")
async def setup_2fa(
    username: str,
    current_user=Depends(get_current_user)
):
    # Admin or self only
    if current_user["role"] != "admin" and current_user["username"] != username:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    users = auth_service.load_users()

    for user in users:

        if user["username"] == username:

            secret = user["totp_secret"]

            totp = pyotp.TOTP(secret)

            provisioning_uri = totp.provisioning_uri(
                name=username,
                issuer_name="AI Face CRM"
            )

            return {
                "secret": secret,
                "qr_url": provisioning_uri
            }

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

@router.get("/users")
async def get_users(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        return {
            "success": False,
            "message": "Admin only"
        }

    users = auth_service.load_users()

    clean_users = []

    for user in users:

        clean_users.append({

            "username": user["username"],
            "role": user["role"],
            "created_at": user["created_at"],
            "last_login" :user["last_login"]

        })

    return {

        "success": True,
        "users": clean_users

    }