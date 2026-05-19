# Login API

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


class CreateUserRequest(BaseModel):

    username: str
    password: str
    role: str = "user"


class ChangePasswordRequest(BaseModel):

    username : str
    new_password: str


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

    token = create_token({
        "username": user["username"],
        "role": user["role"]
    })

    return {
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

    success = auth_service.create_user(
        request.username,
        request.password,
        request.role
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return {
        "message": "User created"
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

    auth_service.change_password(
        request.username,
        request.new_password
    )

    return {
        "message": "Password updated"
    }


@router.get("/me")
async def me(
    current_user=Depends(get_current_user)
):

    return current_user