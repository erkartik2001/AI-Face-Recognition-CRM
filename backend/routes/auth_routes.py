# Login API

from fastapi import APIRouter

from pydantic import BaseModel

from backend.auth.auth_service import AuthService

from backend.auth.auth_handler import create_access_token


router = APIRouter()

auth_service = AuthService()


class LoginRequest(BaseModel):

    username: str
    password: str


@router.post("/login")
async def login(
    request: LoginRequest
):

    user = auth_service.authenticate_user(
        request.username,
        request.password
    )

    if not user:

        return {
            "success": False,
            "message": "Invalid credentials"
        }

    token = create_access_token({
        "sub": user["username"]
    })

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer"
    }