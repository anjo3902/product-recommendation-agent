"""
User Profile Management Routes
Handles user profile updates, password changes, and account management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

from src.database.connection import get_db
from src.database.models import User
from src.utils.middleware import get_current_user
from src.utils.auth import PasswordHasher, AuthValidator

router = APIRouter(prefix="/profile", tags=["User Profile"])


# ==================== REQUEST MODELS ====================

class UpdateProfileRequest(BaseModel):
    """
    Request model for updating user profile
    
    Fields:
    - full_name: User's full name (optional)
    - username: New username (optional)
    
    Example:
    {
        "full_name": "John Smith",
        "username": "john_smith_2026"
    }
    """
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format if provided"""
        if v is not None:
            is_valid, error_msg = AuthValidator.validate_username(v)
            if not is_valid:
                raise ValueError(error_msg)
        return v


class ChangePasswordRequest(BaseModel):
    """
    Request model for changing password
    
    Fields:
    - current_password: User's current password for verification
    - new_password: New password to set
    
    Example:
    {
        "current_password": "OldPass123",
        "new_password": "NewSecurePass456"
    }
    """
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        is_valid, error_msg = AuthValidator.validate_password(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class DeleteAccountRequest(BaseModel):
    """
    Request model for account deletion
    
    Fields:
    - password: User's password for verification
    - confirmation: Must be "DELETE" to confirm deletion
    
    Example:
    {
        "password": "MyPassword123",
        "confirmation": "DELETE"
    }
    """
    password: str = Field(..., min_length=1)
    confirmation: str = Field(..., pattern="^DELETE$")


# ==================== RESPONSE MODELS ====================

class ProfileResponse(BaseModel):
    """
    Response model for profile information
    """
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProfileUpdateResponse(BaseModel):
    """
    Response model for profile update operations
    """
    success: bool
    message: str
    user: ProfileResponse


class PasswordChangeResponse(BaseModel):
    """
    Response model for password change
    """
    success: bool
    message: str


class AccountDeleteResponse(BaseModel):
    """
    Response model for account deletion
    """
    success: bool
    message: str


# ==================== ENDPOINTS ====================

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information
    
    **Authentication Required:** Yes (Bearer token)
    
    **Returns:**
    - User profile with all details
    
    **Example Response:**
    ```json
    {
        "id": 1,
        "email": "user@example.com",
        "username": "john_doe",
        "full_name": "John Doe",
        "created_at": "2026-01-27T12:00:00",
        "last_login": "2026-01-27T12:30:00"
    }
    ```
    """
    return current_user


@router.patch("/", response_model=ProfileUpdateResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    
    **Authentication Required:** Yes (Bearer token)
    
    **Request Body:**
    - full_name (optional): Update full name
    - username (optional): Update username (must be unique)
    
    **Returns:**
    - Updated user profile
    
    **Errors:**
    - 400: Invalid input or username already taken
    - 401: Authentication required
    
    **Example Request:**
    ```json
    {
        "full_name": "John Smith",
        "username": "john_smith_2026"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Profile updated successfully",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "john_smith_2026",
            "full_name": "John Smith",
            "created_at": "2026-01-27T12:00:00",
            "last_login": "2026-01-27T12:30:00"
        }
    }
    ```
    """
    # Check if at least one field is provided
    if request.full_name is None and request.username is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (full_name or username) must be provided"
        )
    
    # Update full name if provided
    if request.full_name is not None:
        current_user.full_name = request.full_name
    
    # Update username if provided
    if request.username is not None:
        # Check if username is different from current
        if request.username != current_user.username:
            # Check if username is already taken
            existing_user = db.query(User).filter(
                User.username == request.username,
                User.id != current_user.id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )
            
            current_user.username = request.username
    
    # Save changes
    db.commit()
    db.refresh(current_user)
    
    return ProfileUpdateResponse(
        success=True,
        message="Profile updated successfully",
        user=ProfileResponse.from_orm(current_user)
    )


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    **Authentication Required:** Yes (Bearer token)
    
    **Request Body:**
    - current_password: Current password for verification
    - new_password: New password (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 400: Invalid password format
    - 401: Current password is incorrect
    
    **Security:**
    - Verifies current password before allowing change
    - New password must meet strength requirements
    - Password is hashed with bcrypt before storage
    
    **Example Request:**
    ```json
    {
        "current_password": "OldPass123",
        "new_password": "NewSecurePass456"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Password changed successfully"
    }
    ```
    """
    # Verify current password
    if not PasswordHasher.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect"
        )
    
    # Check if new password is different from current
    if PasswordHasher.verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password"
        )
    
    # Hash and update password
    new_password_hash = PasswordHasher.hash_password(request.new_password)
    current_user.password_hash = new_password_hash
    
    # Save changes
    db.commit()
    
    return PasswordChangeResponse(
        success=True,
        message="Password changed successfully"
    )


@router.delete("/", response_model=AccountDeleteResponse)
async def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account permanently
    
    **Authentication Required:** Yes (Bearer token)
    
    **Request Body:**
    - password: User's password for verification
    - confirmation: Must be exactly "DELETE" to confirm deletion
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 401: Password is incorrect
    - 400: Confirmation text is incorrect
    
    **Warning:**
    - This action is permanent and cannot be undone
    - All user data will be deleted
    - User will be logged out immediately
    
    **Example Request:**
    ```json
    {
        "password": "MyPassword123",
        "confirmation": "DELETE"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Account deleted successfully"
    }
    ```
    """
    # Verify password
    if not PasswordHasher.verify_password(request.password, current_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Password is incorrect"
        )
    
    # Delete user from database
    db.delete(current_user)
    db.commit()
    
    return AccountDeleteResponse(
        success=True,
        message="Account deleted successfully"
    )


@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """
    Get user account statistics
    
    **Authentication Required:** Yes (Bearer token)
    
    **Returns:**
    - Account age
    - Activity statistics
    
    **Example Response:**
    ```json
    {
        "user_id": 1,
        "username": "john_doe",
        "account_age_days": 45,
        "created_at": "2026-01-27T12:00:00",
        "last_login": "2026-01-27T12:30:00",
        "total_logins": "Available in future version"
    }
    ```
    """
    # Calculate account age
    account_age = datetime.utcnow() - current_user.created_at
    account_age_days = account_age.days
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "account_age_days": account_age_days,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
        "total_logins": "Available in future version",
        "message": "User statistics retrieved successfully"
    }


# ==================== DOCUMENTATION ====================

"""
USAGE EXAMPLES:

1. GET PROFILE:
   GET /profile/
   Headers: Authorization: Bearer <token>

2. UPDATE PROFILE:
   PATCH /profile/
   Headers: 
     Authorization: Bearer <token>
     Content-Type: application/json
   Body: {
     "full_name": "New Name",
     "username": "new_username"
   }

3. CHANGE PASSWORD:
   POST /profile/change-password
   Headers: 
     Authorization: Bearer <token>
     Content-Type: application/json
   Body: {
     "current_password": "OldPass123",
     "new_password": "NewPass456"
   }

4. DELETE ACCOUNT:
   DELETE /profile/
   Headers: 
     Authorization: Bearer <token>
     Content-Type: application/json
   Body: {
     "password": "MyPassword123",
     "confirmation": "DELETE"
   }

5. GET STATS:
   GET /profile/stats
   Headers: Authorization: Bearer <token>
"""
