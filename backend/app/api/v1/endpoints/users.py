"""
Users management endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.schemas import User, UserCreate, UserUpdate
from app.core.logging import logger

router = APIRouter()


@router.get("/", response_model=List[User])
async def list_users():
    """
    List all users (admin only)
    """
    # TODO: Implement user listing
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User listing not yet implemented"
    )


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Get user by ID
    """
    # TODO: Implement get user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user not yet implemented"
    )


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserUpdate):
    """
    Update user
    """
    # TODO: Implement update user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update user not yet implemented"
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """
    Delete user
    """
    # TODO: Implement delete user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete user not yet implemented"
    )
