"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.schemas import Token, User, UserCreate
from app.core.logging import logger

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    # TODO: Implement user registration
    logger.info(f"User registration attempted: {user_data.username}")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration not yet implemented"
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login and get access token
    """
    # TODO: Implement login
    logger.info(f"Login attempted: {form_data.username}")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login not yet implemented"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str):
    """
    Refresh access token
    """
    # TODO: Implement token refresh
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )


@router.get("/me", response_model=User)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user info
    """
    # TODO: Implement get current user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get current user not yet implemented"
    )
