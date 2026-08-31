from fastapi import HTTPException, status
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from backend.app.services.auth_service import auth_service

class AuthController:
    @staticmethod
    async def register(req: UserRegisterRequest) -> TokenResponse:
        try:
            res = await auth_service.register_user(req)
            return TokenResponse(
                access_token=res["access_token"],
                token_type=res["token_type"],
                user=UserResponse(**res["user"])
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code": "INVALID_INPUT", "message": str(e)})

    @staticmethod
    async def login(req: UserLoginRequest) -> TokenResponse:
        try:
            res = await auth_service.login_user(req)
            return TokenResponse(
                access_token=res["access_token"],
                token_type=res["token_type"],
                user=UserResponse(**res["user"])
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_CREDENTIALS", "message": str(e)})

    @staticmethod
    async def get_current_profile(user: dict) -> UserResponse:
        return UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            createdAt=user["createdAt"],
            lastLogin=user.get("lastLogin")
        )
