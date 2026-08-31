from fastapi import APIRouter, Depends
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from backend.app.controllers.auth_controller import AuthController
from backend.app.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest):
    return await AuthController.register(req)

@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest):
    return await AuthController.login(req)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return await AuthController.get_current_profile(current_user)

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Logged out successfully."}
